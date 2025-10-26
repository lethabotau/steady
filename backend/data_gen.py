
#!/usr/bin/env python3
"""
Generate BOTH:
  1) data/context/context.csv  (daily 'weather', 'is_event', 'competition_index')
  2) Per-driver trip-level CSVs (zone-aware), plus optional combined all_trips.csv

This version ALWAYS generates a 42-day window ending on the LAST COMPLETED SUNDAY
in Australia/Sydney time (i.e., end of the previous week). If today is Sunday,
it uses the Sunday from a week ago.

Usage (one command):
  python3 data_gen.py \
    --drivers <number> \
    --zones data/zones.csv \
    --combined \
    --weekend_as_event
"""

import argparse, csv, os, hashlib, uuid, math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


try:
    import zoneinfo  # Python 3.9+
except ImportError:
    from backports import zoneinfo  # type: ignore

# ---------------- deterministic helper ----------------
def h01(*parts: str) -> float:
    """Deterministic pseudo-random in [0,1)."""
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest(), 16) / (2**256)

# ---------------- NSW Holidays (2025) ----------------
HOLIDAYS_NSW = {
    "2025-01-01": "New Year’s Day",
    "2025-01-26": "Australia Day",
    "2025-03-29": "Good Friday",
    "2025-03-30": "Easter Saturday",
    "2025-03-31": "Easter Sunday",
    "2025-04-01": "Easter Monday",
    "2025-04-25": "Anzac Day",
    "2025-06-10": "King’s Birthday",
    "2025-10-07": "Labour Day",
    "2025-12-25": "Christmas Day",
    "2025-12-26": "Boxing Day",
}

# ---------------- CLI ----------------
def parse_args():
    p = argparse.ArgumentParser(description="Generate context + per-driver, zone-aware trip data (self-contained).")
    # Core controls
    p.add_argument("--drivers", type=int, default=5)
    # --days/--start kept for compatibility but we always compute 42 days ending last Sunday
    p.add_argument("--days", type=int, default=42, help="Ignored: always 42 ending last completed Sunday")
    p.add_argument("--start", type=str, default="", help="Ignored: auto-computed to end last Sunday")
    p.add_argument("--outdir", type=str, default="data")
    p.add_argument("--seed", type=str, default="steady")
    p.add_argument("--combined", action="store_true", help="Also write data/all_trips.csv")
    # Zones
    p.add_argument("--zones", type=str, required=True,
                   help="CSV: zone_id,zone_name,lat,lng,radius_km,base_demand,weekend_mult,rain_mult,event_mult")
    # Context (either provide a CSV, or we build one inline)
    p.add_argument("--context", type=str, default=None,
                   help="Existing context CSV (date,weather,is_event,competition_index). If omitted, we'll build one.")
    p.add_argument("--context_out", type=str, default="data/context/context.csv",
                   help="Where to write the auto-generated context.csv (if --context not supplied).")
    p.add_argument("--rain_prob", type=float, default=0.22, help="Base daily rain probability (auto-context).")
    p.add_argument("--weekend_as_event", action="store_true", help="Mark weekends as events (auto-context).")
    # Behavior knobs
    p.add_argument("--base_daily_hours_min", type=float, default=4.0)
    p.add_argument("--base_daily_hours_max", type=float, default=9.5)
    p.add_argument("--weekend_hours_mult", type=float, default=1.12)
    p.add_argument("--rain_hours_mult", type=float, default=0.95)
    p.add_argument("--event_hours_mult", type=float, default=1.05)

    p.add_argument("--thr_base_min", type=float, default=1.0, help="trips/hour baseline min")
    p.add_argument("--thr_base_max", type=float, default=2.0, help="trips/hour baseline max")
    p.add_argument("--weekend_demand_mult", type=float, default=1.10)
    p.add_argument("--rain_demand_mult", type=float, default=1.08)
    p.add_argument("--event_demand_mult", type=float, default=1.12)
    p.add_argument("--competition_slope", type=float, default=0.30)  # demand *= (1 - slope*competition)

    p.add_argument("--cancel_rate_min", type=float, default=0.01)
    p.add_argument("--cancel_rate_max", type=float, default=0.07)

    # surge bounds
    p.add_argument("--surge_weekend", type=float, default=1.06)
    p.add_argument("--surge_rain_low", type=float, default=1.10)
    p.add_argument("--surge_rain_high", type=float, default=1.35)
    p.add_argument("--surge_event_low", type=float, default=1.08)
    p.add_argument("--surge_event_high", type=float, default=1.25)
    return p.parse_args()

# ---------------- utils ----------------
def ensure_dir(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def write_csv(path: str, rows: List[Dict], cols: List[str]):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def daterange_days(start: datetime, n: int):
    for i in range(n):
        yield start + timedelta(days=i)

def load_context(path: Optional[str]) -> Dict[str, Dict]:
    if not path:
        return {}
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            date = row["date"]
            out[date] = {
                "date": date,
                "weather": (row.get("weather") or "clear").strip().lower(),
                "is_event": int(float(row.get("is_event", 0))),
                "competition_index": float(row.get("competition_index", 0.4)),
            }
    return out

# --------- auto-build context if --context not provided ----------
def build_context_inline(start_date: str, days: int, out_path: str,
                         rain_prob: float, weekend_as_event: bool, seed: str) -> Dict[str, Dict]:
    """Generate simple context.csv (weather, weekends+holidays events, competition) and return dict."""
    ensure_dir(os.path.dirname(out_path))
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    rows: List[Dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        ds = d.isoformat()
        dow = d.weekday()  # 0=Mon..6=Sun

        # Weather: seasonal + deterministic
        seasonal = 0.05 * math.sin(2 * math.pi * (d.timetuple().tm_yday) / 365.0)
        u = h01(seed, ds, "rain")
        p_rain = max(0.0, min(1.0, rain_prob + seasonal))
        is_rain = 1 if u < p_rain else 0
        weather = "rain" if is_rain else "clear"

        # Event: weekend and/or NSW holiday
        is_weekend = (dow in (5, 6)) if weekend_as_event else False
        is_holiday = (ds in HOLIDAYS_NSW)
        is_event = 1 if (is_weekend or is_holiday) else 0

        # Competition: weekday > weekend; rain lowers a bit; weekly wave
        weekly_wave = 0.12 * math.sin(2 * math.pi * (dow / 7.0))
        base = 0.5 + weekly_wave
        base += (-0.08 if is_rain else +0.03)
        comp = round(max(0.0, min(1.0, base)), 2)

        rows.append({
            "date": ds,
            "weather": weather,
            "is_event": is_event,
            "competition_index": comp,
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","weather","is_event","competition_index"])
        w.writeheader(); w.writerows(rows)
    print(f"Auto-context: wrote {len(rows)} rows → {out_path}")
    return {r["date"]: r for r in rows}

# ---------------- demand shape ----------------
def tod_intensity(minute_of_day: int) -> float:
    """Time-of-day intensity: commute (8-10), dinner (17-20), late night tail."""
    m = minute_of_day
    def gauss(mu, sigma):
        from math import exp
        return exp(-0.5 * ((m - mu) / sigma) ** 2)
    morning = gauss(9*60, 90)
    evening = gauss(18*60, 120)
    late    = gauss(23*60, 150) * 0.5
    base    = 0.25
    return base + morning + evening + late

def weighted_random_minute(seed_key: str, start_min: int, end_min: int) -> int:
    """Pick a minute in [start_min, end_min) proportional to tod_intensity, deterministically."""
    span = max(1, end_min - start_min)
    best_m, best_score = start_min, -1
    for k in range(6):
        u = h01(seed_key, f"cand{k}")
        cand = start_min + int(u * span)
        score = tod_intensity(cand) * (0.9 + 0.2 * h01(seed_key, f"j{k}"))
        if score > best_score:
            best_score, best_m = score, cand
    return best_m

# ---------------- zones & geo ----------------
def load_zones(path: str) -> List[Dict]:
    zones = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            zones.append({
                "zone_id": row["zone_id"],
                "zone_name": row["zone_name"],
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
                "radius_km": float(row["radius_km"]),
                "base_demand": float(row["base_demand"]),
                "weekend_mult": float(row["weekend_mult"]),
                "rain_mult": float(row["rain_mult"]),
                "event_mult": float(row["event_mult"]),
            })
    if not zones:
        raise ValueError("zones.csv is empty.")
    return zones

KM_PER_DEG_LAT = 110.574
KM_PER_DEG_LNG_AT_SYD = 111.320 * math.cos(math.radians(-33.86))

def sample_point_in_circle(lat: float, lng: float, radius_km: float, key: str) -> Tuple[float, float]:
    """Uniform-ish sample within a circle around (lat,lng), deterministic."""
    r_u = h01(key, "r")
    theta = 2 * math.pi * h01(key, "t")
    r_km = radius_km * math.sqrt(r_u)
    dlat = (r_km / KM_PER_DEG_LAT) * math.cos(theta)
    dlng = (r_km / KM_PER_DEG_LNG_AT_SYD) * math.sin(theta)
    return round(lat + dlat, 6), round(lng + dlng, 6)

def pick_zone(zones: List[Dict], is_weekend: bool, weather: str, is_event: int,
              competition_index: float, seed_key: str) -> Dict:
    """Weighted lottery over zones using base_demand + modifiers; deterministic."""
    weights = []
    for z in zones:
        w = z["base_demand"]
        if is_weekend: w *= z["weekend_mult"]
        if weather == "rain": w *= z["rain_mult"]
        if is_event: w *= z["event_mult"]
        w *= max(0.6, 1.0 - 0.3 * competition_index)
        w *= (0.95 + 0.10 * h01(seed_key, z["zone_id"]))
        weights.append(max(0.0001, w))
    total = sum(weights)
    u = h01(seed_key, "choice") * total
    acc = 0.0
    for i, w in enumerate(weights):
        acc += w
        if u <= acc:
            return zones[i]
    return zones[-1]

# ---------------- core per-day trip synthesis ----------------
def synth_trips_for_day(
    driver_id: str,
    dt: datetime,
    seed: str,
    ctx: Dict,
    zones: List[Dict],
    args
) -> List[Dict]:
    date_str = dt.date().isoformat()
    dow = dt.weekday()
    is_weekend = 1 if dow >= 5 or dow == 4 else 0
    weather = ctx.get("weather", "clear")
    is_event = int(ctx.get("is_event", 0))
    comp = float(ctx.get("competition_index", 0.4))

    # hours online
    base_hours = args.base_daily_hours_min + (args.base_daily_hours_max - args.base_daily_hours_min) * h01(seed, driver_id, "base_hours")
    ripple = 0.85 + 0.3 * h01(seed, driver_id, date_str, "hours_ripple")
    hours = base_hours * ripple
    if is_weekend: hours *= args.weekend_hours_mult
    if weather == "rain": hours *= args.rain_hours_mult
    if is_event: hours *= args.event_hours_mult
    hours = max(2.0, min(12.0, hours))
    online_minutes = int(round(hours * 60))

    # throughput / demand -> trips offered
    thr_base = args.thr_base_min + (args.thr_base_max - args.thr_base_min) * h01(seed, driver_id, "thr_base")
    demand_mult = 1.0
    if is_weekend: demand_mult *= args.weekend_demand_mult
    if weather == "rain": demand_mult *= args.rain_demand_mult
    if is_event: demand_mult *= args.event_demand_mult
    demand_mult *= max(0.6, 1.0 - args.competition_slope * comp)
    demand_mult *= 0.9 + 0.2 * h01(seed, driver_id, date_str, "demand_ripple")
    trips_offered = max(0, int(round((online_minutes / 60.0) * thr_base * demand_mult)))

    # cancellations
    cancel_rate = args.cancel_rate_min + (args.cancel_rate_max - args.cancel_rate_min) * h01(seed, driver_id, "cancel_rate")
    trips_canceled = min(trips_offered, int(round(trips_offered * cancel_rate * (0.95 + 0.1 * (1 if weather == "rain" else 0)))))
    trips_completed = trips_offered - trips_canceled

    rows: List[Dict] = []

    # choose an online window (start 06:00–14:00)
    day0 = datetime.fromisoformat(date_str + "T00:00:00")
    online_start_min = 6*60 + int(h01(seed, driver_id, date_str, "start") * (8*60))  # 06:00..14:00
    online_end_min = min(23*60+59, online_start_min + online_minutes)

    # surge multiplier base for day
    surge = 1.0
    if is_weekend: surge *= args.surge_weekend
    if weather == "rain":
        surge *= (args.surge_rain_low + (args.surge_rain_high - args.surge_rain_low) * h01(seed, date_str, "rain_surge"))
    if is_event:
        surge *= (args.surge_event_low + (args.surge_event_high - args.surge_event_low) * h01(seed, date_str, "event_surge"))
    surge *= (0.95 + 0.10 * h01(seed, driver_id, date_str, "surge_noise"))
    surge = max(1.0, min(1.9, surge))

    # completed trips
    for k in range(trips_completed):
        key = f"{driver_id}|{date_str}|{k}|{seed}"

        # timestamps
        start_min = weighted_random_minute(key, online_start_min, online_end_min)
        dur = int(8 + (35 - 8) * h01(key, "dur"))
        end_min = min(online_end_min, start_min + dur)

        # zone selection
        z_pick = pick_zone(zones, bool(is_weekend), weather, is_event, comp, key)
        z_drop = z_pick if h01(key, "stay") < 0.7 else pick_zone(zones, bool(is_weekend), weather, is_event, comp, key+"drop")

        # coordinates inside chosen zones
        pickup_lat, pickup_lng = sample_point_in_circle(z_pick["lat"], z_pick["lng"], z_pick["radius_km"], key+"p")
        drop_lat, drop_lng     = sample_point_in_circle(z_drop["lat"], z_drop["lng"], z_drop["radius_km"], key+"d")

        # distance loosely tied to duration + inter-zone bump
        base_km = (dur / 3.0) * (0.8 + 0.4 * h01(key, "km"))
        interzone_bump = 1.15 if z_pick["zone_id"] != z_drop["zone_id"] else 1.0
        distance_km = round(base_km * interzone_bump, 2)

        # zone nudge on surge (hot zones → slightly higher)
        zone_surge = surge * (0.98 + 0.06 * (z_pick["base_demand"] - 1.0))
        zone_surge = max(1.0, min(2.0, zone_surge))

        # fare components
        fare_base = round(3.5 + 2.5 * h01(driver_id, "fare_base"), 2)
        fare_time_coef = 0.8 + 0.8 * h01(driver_id, "fare_time")
        fare_dist_coef = 3.5 + 4.5 * h01(driver_id, "fare_dist")
        fare_time = round(fare_time_coef * (dur / 10.0), 2)
        fare_dist = round(fare_dist_coef * (distance_km / 5.0), 2)
        fare_total = max(6.0, round((fare_base + fare_time + fare_dist) * zone_surge, 2))

        # tips: higher on weekend & with surge; TOD helps
        tod_weight = 0.8 + 0.4 * tod_intensity(start_min)
        tip_prob = 0.14 * tod_weight * (1.05 if is_weekend else 1.0) * (1.0 + 0.12 * (zone_surge - 1.0))
        tipped = h01(key, "tip") < min(0.9, tip_prob)
        tip_amount = round((1.0 + 5.0 * h01(key, "tip_amt")) * (1.0 + 0.1 * (zone_surge - 1.0)), 2) if tipped else 0.0

        # platform/service fee (on fare, not tips)
        fee_rate = 0.24 + 0.06 * h01(driver_id, "fee_rate")
        service_fee = round(fare_total * fee_rate, 2)

        driver_earnings = round(fare_total - service_fee + tip_amount, 2)

        rows.append({
            "driver_id": driver_id,
            "trip_id": str(uuid.uuid4()),
            "date": date_str,
            "pickup_timestamp": (day0 + timedelta(minutes=start_min)).isoformat(),
            "dropoff_timestamp": (day0 + timedelta(minutes=end_min)).isoformat(),
            "is_canceled": 0,
            "is_weekend": is_weekend,
            "is_rain": 1 if weather == "rain" else 0,
            "is_event": is_event,
            "pickup_zone": z_pick["zone_id"],
            "pickup_zone_name": z_pick["zone_name"],
            "dropoff_zone": z_drop["zone_id"],
            "dropoff_zone_name": z_drop["zone_name"],
            "surge_multiplier": round(zone_surge, 3),
            "surge_applied": 1 if zone_surge > 1.0 else 0,
            "distance_km": distance_km,
            "duration_min": end_min - start_min,
            "fare_base": fare_base,
            "fare_time": fare_time,
            "fare_distance": fare_dist,
            "fare_total": fare_total,
            "tip_amount": tip_amount,
            "cancel_fee": 0.0,
            "service_fee": service_fee,
            "driver_earnings": driver_earnings,
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "dropoff_lat": drop_lat,
            "dropoff_lng": drop_lng
        })

    # canceled trips (assign a pickup zone, no dropoff)
    for k in range(trips_canceled):
        key = f"{driver_id}|{date_str}|c{k}|{seed}"
        z_pick = pick_zone(zones, bool(is_weekend), weather, is_event, comp, key)
        tmin = weighted_random_minute(key, online_start_min, online_end_min)
        cancel_fee = round(5.0 + 7.0 * h01(key, "cfee"), 2) if h01(key, "has_cfee") < 0.25 else 0.0
        pickup_lat, pickup_lng = sample_point_in_circle(z_pick["lat"], z_pick["lng"], z_pick["radius_km"], key+"p")

        rows.append({
            "driver_id": driver_id,
            "trip_id": str(uuid.uuid4()),
            "date": date_str,
            "pickup_timestamp": (day0 + timedelta(minutes=tmin)).isoformat(),
            "dropoff_timestamp": (day0 + timedelta(minutes=tmin)).isoformat(),
            "is_canceled": 1,
            "is_weekend": is_weekend,
            "is_rain": 1 if weather == "rain" else 0,
            "is_event": is_event,
            "pickup_zone": z_pick["zone_id"],
            "pickup_zone_name": z_pick["zone_name"],
            "dropoff_zone": None,
            "dropoff_zone_name": None,
            "surge_multiplier": 1.0,
            "surge_applied": 0,
            "distance_km": 0.0,
            "duration_min": 0,
            "fare_base": 0.0,
            "fare_time": 0.0,
            "fare_distance": 0.0,
            "fare_total": 0.0,
            "tip_amount": 0.0,
            "cancel_fee": cancel_fee,
            "service_fee": 0.0,
            "driver_earnings": cancel_fee,
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "dropoff_lat": None,
            "dropoff_lng": None
        })

    rows.sort(key=lambda r: r["pickup_timestamp"])
    return rows

# ---------------- main ----------------
def main():
    args = parse_args()
    ensure_dir(args.outdir)

    # Compute the 42-day window ending LAST COMPLETED SUNDAY in Australia/Sydney
    syd = zoneinfo.ZoneInfo("Australia/Sydney")
    today = datetime.now(syd).date()
    # Monday=0 .. Sunday=6 ; days since most recent Sunday:
    days_since_sunday = (today.weekday() + 1) % 7
    # Last completed Sunday = if today is Sunday, go back 7 days; else, go back to that Sunday
    last_sunday = today - timedelta(days=days_since_sunday or 7)
    end_date = last_sunday
    DAYS = 42
    start_date = end_date - timedelta(days=DAYS - 1)

    # Overwrite any provided start/days with the aligned window
    args.days = DAYS
    args.start = start_date.isoformat()
    print(f"Window: {args.start} → {end_date.isoformat()} (42 days, AU/Sydney, aligned to last Sunday)")

    # 1) Zones (required)
    zones = load_zones(args.zones)

    # 2) Context: use provided file OR build inline
    if args.context:
        context = load_context(args.context)
        print(f"Using existing context: {args.context} ({len(context)} days)")
    else:
        context = build_context_inline(
            start_date=args.start,
            days=args.days,
            out_path=args.context_out,
            rain_prob=args.rain_prob,
            weekend_as_event=args.weekend_as_event,
            seed=args.seed,
        )

    start_dt = datetime.strptime(args.start, "%Y-%m-%d")

    cols = [
        "driver_id","trip_id","date",
        "pickup_timestamp","dropoff_timestamp",
        "is_canceled","is_weekend","is_rain","is_event",
        "pickup_zone","pickup_zone_name","dropoff_zone","dropoff_zone_name",
        "surge_multiplier","surge_applied",
        "distance_km","duration_min",
        "fare_base","fare_time","fare_distance","fare_total",
        "tip_amount","cancel_fee","service_fee","driver_earnings",
        "pickup_lat","pickup_lng","dropoff_lat","dropoff_lng"
    ]

    combined: List[Dict] = []

    for i in range(1, args.drivers + 1):
        driver_id = f"D{i:04d}"
        driver_rows: List[Dict] = []
        for d in daterange_days(start_dt, args.days):
            ctx = context.get(d.date().isoformat(), {})
            driver_rows.extend(synth_trips_for_day(driver_id, d, args.seed, ctx, zones, args))
        write_csv(os.path.join(args.outdir, f"driver_{driver_id}_trips.csv"), driver_rows, cols)
        if args.combined:
            combined.extend(driver_rows)

    if args.combined:
        write_csv(os.path.join(args.outdir, "all_trips.csv"), combined, cols)

    print(f"Generated {args.drivers} drivers × {args.days} days (zone-aware).")
    if args.combined:
        print(f"Wrote combined file: {os.path.abspath(os.path.join(args.outdir, 'all_trips.csv'))}")

if __name__ == "__main__":
    main()


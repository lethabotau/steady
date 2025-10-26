#!/usr/bin/env python3
import requests, csv, json, os
from datetime import date

# -------- Config --------
lat, lng = -33.8688, 151.2093   # Sydney
start_date = "2024-01-01"
end_date = "2024-01-31"
timezone = "Australia/Sydney"
outdir = "data/context"
os.makedirs(outdir, exist_ok=True)

# -------- API Call --------
url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lng}"
    f"&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
    f"&start_date={start_date}&end_date={end_date}"
    f"&timezone={timezone}"
)
resp = requests.get(url)
resp.raise_for_status()
data = resp.json()

# Save raw JSON
with open(f"{outdir}/raw_weather.json", "w") as f:
    json.dump(data, f, indent=2)

# -------- Transform → context.csv --------
dates = data["daily"]["time"]
rain = data["daily"]["precipitation_sum"]

rows = []
for d, r in zip(dates, rain):
    weather = "rain" if r > 3 else "clear"
    rows.append({
        "date": d,
        "weather": weather,
        "is_event": 0,
        "competition_index": round(0.4 + 0.2 * (hash(d) % 100) / 100, 2)
    })

with open(f"{outdir}/context.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["date","weather","is_event","competition_index"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} days to {outdir}/context.csv")

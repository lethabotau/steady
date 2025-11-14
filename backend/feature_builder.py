import os
import glob
import pandas as pd

def load_context(context_path: str) -> pd.DataFrame:
    """Load daily weather, event, and competition data."""
    context_data = pd.read_csv(context_path)
    context_data["date"] = pd.to_datetime(context_data["date"]).dt.date
    context_data["is_event"] = context_data["is_event"].astype(int)
    context_data["weather"] = context_data["weather"].astype(str).str.lower().str.strip()
    return context_data[["date", "weather", "is_event", "competition_index"]]


def load_trip_data(trip_pattern: str) -> pd.DataFrame:
    """Load all per-driver trip CSVs matching pattern."""
    trip_files = sorted(glob.glob(trip_pattern))
    if not trip_files:
        raise SystemExit("No trip data found.")
    all_trips = []
    for file in trip_files:
        df = pd.read_csv(file, parse_dates=["pickup_timestamp", "dropoff_timestamp"])
        all_trips.append(df)
    return pd.concat(all_trips, ignore_index=True)


def build_hourly_features(trip_data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate trip-level data into hourly features per driver."""
    trip_data = trip_data.copy()
    pickup_times = trip_data["pickup_timestamp"]

    # Calendar fields
    trip_data["date"] = pickup_times.dt.date
    trip_data["hour"] = pickup_times.dt.hour
    trip_data["day_of_week"] = pd.to_datetime(trip_data["date"]).dt.dayofweek
    trip_data["is_weekend"] = (trip_data["day_of_week"] >= 5).astype(int)

    # Completed vs canceled
    completed = trip_data[trip_data["is_canceled"] == 0]
    canceled = trip_data[trip_data["is_canceled"] == 1]

    group_cols = ["driver_id", "date", "hour", "day_of_week", "is_weekend"]

    # Aggregate completed trips
    completed_summary = (
        completed.groupby(group_cols, as_index=False)
        .agg(
            total_trips=("trip_id", "count"),
            total_earnings=("driver_earnings", "sum"),
            total_minutes_worked=("duration_min", "sum"),
            average_surge=("surge_multiplier", "mean"),
            any_rain=("is_rain", "max"),
        )
    )

    # Aggregate canceled trips
    canceled_summary = (
        canceled.groupby(group_cols, as_index=False)
        .agg(total_canceled_trips=("trip_id", "count"))
    )

    # Merge both
    features = completed_summary.merge(canceled_summary, on=group_cols, how="left")
    features["total_canceled_trips"] = features["total_canceled_trips"].fillna(0).astype(int)
    features["average_surge"] = features["average_surge"].fillna(0)
    features["any_rain"] = features["any_rain"].fillna(0).astype(int)

    return features.sort_values(group_cols).reset_index(drop=True)


def save_features(features: pd.DataFrame, output_dir: str) -> None:
    """Write one feature file per driver."""
    os.makedirs(output_dir, exist_ok=True)
    output_columns = [
        "driver_id", "date", "hour", "day_of_week", "is_weekend",
        "total_trips", "total_canceled_trips", "total_minutes_worked",
        "total_earnings", "average_surge", "any_rain",
        "weather", "is_event", "competition_index",
    ]
    for driver_id, df in features.groupby("driver_id"):
        df[output_columns].to_csv(
            os.path.join(output_dir, f"{driver_id}_hourly.csv"),
            index=False,
        )


def main():
    data_dir = "data"
    context_path = os.path.join(data_dir, "context/context.csv")
    trip_pattern = os.path.join(data_dir, "driver_*.csv")
    output_dir = "features"

    context = load_context(context_path)
    trips = load_trip_data(trip_pattern)
    features = build_hourly_features(trips)

    features = features.merge(context, on="date", how="left")
    features["weather"] = features["weather"].fillna("clear")
    features["is_event"] = features["is_event"].fillna(0).astype(int)
    features["competition_index"] = features["competition_index"].fillna(0.4)

    save_features(features, output_dir)

    print(f"\nFeatures generated in '{output_dir}/'")
    print(f"Rows: {len(features):,}")
    print(f"Drivers: {features['driver_id'].nunique()}")
    print(f"Dates: {features['date'].nunique()}\n")


if __name__ == "__main__":
    main()

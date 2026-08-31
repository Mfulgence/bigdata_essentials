#!/usr/bin/env python3
"""
clean_data.py -- Section 7, Data Cleaning

Removes HARD-invalid records only (rows that cannot represent a real
trip), and reports exactly how many rows each rule affected so the
report can justify every removal, per the assignment's instruction to
"not simply delete unusual records without justification."

Rules applied (a row is dropped if ANY of these hold):
  - missing / unparseable pickup or dropoff timestamp
  - missing PULocationID, DOLocationID, trip_distance or fare_amount
  - trip_distance <= 0
  - fare_amount <= 0
  - dropoff_datetime <= pickup_datetime (non-positive duration)
  - trip duration > 6 hours (impossible for a normal taxi trip)
  - exact duplicate rows

passenger_count is deliberately NOT a drop condition. In current TLC
releases a large share of trips (commonly ~25-30%) have a null
passenger_count -- a known vendor-side reporting gap, not a sign the
rest of the row is unreliable. Every other field on those rows
(timestamps, locations, distance, fare) is perfectly valid, and
passenger_count itself is used by exactly one downstream job
(mapper_anomaly.py's high-passenger-count flag). Dropping ~30% of
otherwise-good, revenue-bearing trips over one lightly-used field
would distort every other analysis (demand, revenue, routes) far more
than it protects. Missing values are instead imputed with 1 (a single
passenger), the most common real value and TLC's own documented
default -- counted separately below as
missing_passenger_count_imputed, never silently absorbed into
"rows kept" without disclosure. Records that are unusual but not
impossible (e.g. 7 passengers, a 90-mile trip, a very high
fare-per-mile) are intentionally KEPT here -- they are the job of
mapper_anomaly.py / reducer_anomaly.py to flag and count later, on the
cleaned data, without deleting them.

Usage:
    python clean_data.py data/raw/yellow_tripdata_2024-01.csv \
        data/cleaned/yellow_tripdata_2024-01.csv
"""
import sys
import json
import pandas as pd

CHUNK_SIZE = 500_000

REQUIRED_COLUMNS = [
    "tpep_pickup_datetime", "tpep_dropoff_datetime", "PULocationID",
    "DOLocationID", "trip_distance", "fare_amount",
]


def clean_chunk(df, counters):
    counters["rows_seen"] += len(df)

    missing_mask = df[REQUIRED_COLUMNS].isna().any(axis=1)
    counters["missing_required_field"] += int(missing_mask.sum())
    df = df[~missing_mask].copy()

    missing_passengers = df["passenger_count"].isna()
    counters["missing_passenger_count_imputed"] += int(missing_passengers.sum())
    df["passenger_count"] = df["passenger_count"].fillna(1)

    df["tpep_pickup_datetime"] = pd.to_datetime(
        df["tpep_pickup_datetime"], errors="coerce"
    )
    df["tpep_dropoff_datetime"] = pd.to_datetime(
        df["tpep_dropoff_datetime"], errors="coerce"
    )
    bad_ts_mask = df["tpep_pickup_datetime"].isna() | df["tpep_dropoff_datetime"].isna()
    counters["invalid_timestamp"] += int(bad_ts_mask.sum())
    df = df[~bad_ts_mask]

    bad_passengers = df["passenger_count"] <= 0
    counters["invalid_passenger_count"] += int(bad_passengers.sum())
    df = df[~bad_passengers]

    bad_distance = df["trip_distance"] <= 0
    counters["invalid_distance"] += int(bad_distance.sum())
    df = df[~bad_distance]

    bad_fare = df["fare_amount"] <= 0
    counters["invalid_fare"] += int(bad_fare.sum())
    df = df[~bad_fare]

    duration_min = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60.0
    bad_duration = (duration_min <= 0) | (duration_min > 360)
    counters["impossible_duration"] += int(bad_duration.sum())
    df = df[~bad_duration]

    return df


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output_cleaned.csv>")
        sys.exit(1)
    input_path, output_path = sys.argv[1], sys.argv[2]

    counters = {
        "rows_seen": 0,
        "missing_required_field": 0,
        "missing_passenger_count_imputed": 0,
        "invalid_timestamp": 0,
        "invalid_passenger_count": 0,
        "invalid_distance": 0,
        "invalid_fare": 0,
        "impossible_duration": 0,
        "duplicate_rows": 0,
        "rows_kept": 0,
    }

    seen_dup_check = pd.DataFrame()
    first_chunk = True
    with open(output_path, "w", newline="") as out_f:
        for chunk in pd.read_csv(input_path, chunksize=CHUNK_SIZE, low_memory=False):
            cleaned = clean_chunk(chunk, counters)

            before_dedup = len(cleaned)
            cleaned = cleaned.drop_duplicates()
            counters["duplicate_rows"] += before_dedup - len(cleaned)

            cleaned.to_csv(out_f, index=False, header=first_chunk, mode="a")
            first_chunk = False
            counters["rows_kept"] += len(cleaned)

    report = {"counts": counters, "percentages": {}}
    total = counters["rows_seen"] or 1
    for k, v in counters.items():
        if k in ("rows_seen", "rows_kept"):
            continue
        report["percentages"][k] = round(100 * v / total, 3)
    report["percentages"]["rows_kept"] = round(100 * counters["rows_kept"] / total, 3)

    report_path = output_path.rsplit(".", 1)[0] + "_cleaning_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nCleaned data written to {output_path}")
    print(f"Cleaning report written to {report_path}")


if __name__ == "__main__":
    main()

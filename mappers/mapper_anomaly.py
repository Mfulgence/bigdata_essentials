#!/usr/bin/env python3
"""
mapper_anomaly.py -- Analysis (i) Anomaly Detection

This job runs on the CLEANED dataset (input/cleaned), i.e. AFTER
scripts/clean_data.py has already dropped hard-invalid rows (nulls,
negative fares/distances, dropoff-before-pickup, duplicates -- see
Section 7 of the assignment). What's left here are records that are
technically valid but statistically suspicious, which the assignment
explicitly says NOT to silently delete -- we count and categorize them
instead so the report can discuss them with justification.

KEY   = anomaly type, one of:
          high_passenger_count   (> 6 passengers)
          long_distance           (> 100 miles)
          long_duration           (> 180 minutes)
          low_fare_per_mile       (< $1.00 / mile)
          high_fare_per_mile      (> $50.00 / mile)
          normal                  (none of the above)
VALUE = 1

A single trip can trigger more than one rule, so it can be emitted
under more than one key -- the reducer's total across all non-"normal"
keys therefore counts *flag events*, not unique trips. The report
divides by the run's total trip count (from the hourly job) to get a
percentage of affected records; this is explained in WALKTHROUGH.md.
"""
import sys
import csv
from datetime import datetime

COL_PICKUP_DT = 1
COL_DROPOFF_DT = 2
COL_PASSENGERS = 3
COL_DISTANCE = 4
COL_FARE = 10


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_FARE:
            continue
        try:
            int(row[0])
            pickup = datetime.strptime(row[COL_PICKUP_DT], "%Y-%m-%d %H:%M:%S")
            dropoff = datetime.strptime(row[COL_DROPOFF_DT], "%Y-%m-%d %H:%M:%S")
            passengers = int(float(row[COL_PASSENGERS]))
            distance = float(row[COL_DISTANCE])
            fare = float(row[COL_FARE])
        except (ValueError, IndexError):
            continue

        minutes = (dropoff - pickup).total_seconds() / 60.0
        fare_per_mile = fare / distance if distance > 0 else None

        flags = []
        if passengers > 6:
            flags.append("high_passenger_count")
        if distance > 100:
            flags.append("long_distance")
        if minutes > 180:
            flags.append("long_duration")
        if fare_per_mile is not None:
            if fare_per_mile < 1.0:
                flags.append("low_fare_per_mile")
            elif fare_per_mile > 50.0:
                flags.append("high_fare_per_mile")

        if not flags:
            flags = ["normal"]

        for flag in flags:
            print(f"{flag}\t1")


if __name__ == "__main__":
    main()

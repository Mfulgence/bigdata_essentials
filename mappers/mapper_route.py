#!/usr/bin/env python3
"""
mapper_route.py -- Analysis (g) Busiest Pickup-Drop-off Routes

KEY   = route key, "PULocationID-DOLocationID" (e.g. "132-236")
VALUE = "fare_amount,total_amount,1"

Combining two IDs into a single composite key is a common MapReduce
pattern for "analysis grouped by a pair of things" -- there is nothing
special about it beyond string concatenation, but it's worth being able
to explain because the instructor may ask "why not two keys?": Hadoop
Streaming keys are just text, so a composite string key is the simplest
way to group by (origin, destination) together.
"""
import sys
import csv

COL_PU_LOCATION = 7
COL_DO_LOCATION = 8
COL_FARE = 10
COL_TOTAL = 16


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_TOTAL:
            continue
        try:
            int(row[0])
            pu_id = int(row[COL_PU_LOCATION])
            do_id = int(row[COL_DO_LOCATION])
            fare = float(row[COL_FARE])
            total = float(row[COL_TOTAL])
        except (ValueError, IndexError):
            continue

        print(f"{pu_id}-{do_id}\t{fare},{total},1")


if __name__ == "__main__":
    main()

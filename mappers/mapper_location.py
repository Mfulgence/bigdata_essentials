#!/usr/bin/env python3
"""
mapper_location.py -- Analysis (c) Pickup Location Analysis

KEY   = PULocationID (zone ID, 1-263 in the TLC taxi zone lookup table)
VALUE = 1

We key by the raw zone ID rather than the zone name to keep the mapper
independent of any lookup table. Zone IDs are joined to human-readable
names (Borough/Zone) locally afterwards using taxi_zone_lookup.csv --
see scripts/join_zone_names.py in the README.
"""
import sys
import csv

COL_PU_LOCATION = 7


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_PU_LOCATION:
            continue
        try:
            int(row[0])
            pu_id = int(row[COL_PU_LOCATION])
        except (ValueError, IndexError):
            continue

        print(f"{pu_id}\t1")


if __name__ == "__main__":
    main()

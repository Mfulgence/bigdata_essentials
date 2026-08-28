#!/usr/bin/env python3
"""
mapper_revenue.py -- Analysis (d) Revenue by Pickup Location
Also serves as JOB 1 of the compulsory two-stage MapReduce workflow
(see multistage/ for JOB 2, which finds the top-10 zones by revenue).

KEY   = PULocationID
VALUE = "fare_amount,tip_amount,total_amount,trip_distance,1"

We pack five numbers into one comma-joined value string because Hadoop
Streaming's protocol is plain text key\tvalue -- there is no structured
value type, so the reducer will split this string back apart itself.
"""
import sys
import csv

COL_PU_LOCATION = 7
COL_FARE = 10
COL_TIP = 13
COL_TOTAL = 16
COL_DISTANCE = 4


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_TOTAL:
            continue
        try:
            int(row[0])
            pu_id = int(row[COL_PU_LOCATION])
            fare = float(row[COL_FARE])
            tip = float(row[COL_TIP])
            total = float(row[COL_TOTAL])
            distance = float(row[COL_DISTANCE])
        except (ValueError, IndexError):
            continue

        print(f"{pu_id}\t{fare},{tip},{total},{distance},1")


if __name__ == "__main__":
    main()

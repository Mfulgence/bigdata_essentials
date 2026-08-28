#!/usr/bin/env python3
"""
mapper_duration.py -- Analysis (h) Trip Duration Analysis

KEY   = duration bucket: "0-5", "5-15", "15-30", "30-60", "60+" (minutes)
VALUE = "fare_amount,trip_distance,tip_amount,1"

Durations <= 0 or > 6 hours are skipped here as hard-invalid (already
supposed to have been removed during data cleaning); anything left is a
plausible trip we want bucketed.
"""
import sys
import csv
from datetime import datetime

COL_PICKUP_DT = 1
COL_DROPOFF_DT = 2
COL_DISTANCE = 4
COL_FARE = 10
COL_TIP = 13


def bucket(minutes):
    if minutes <= 5:
        return "0-5"
    if minutes <= 15:
        return "5-15"
    if minutes <= 30:
        return "15-30"
    if minutes <= 60:
        return "30-60"
    return "60+"


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_TIP:
            continue
        try:
            int(row[0])
            pickup = datetime.strptime(row[COL_PICKUP_DT], "%Y-%m-%d %H:%M:%S")
            dropoff = datetime.strptime(row[COL_DROPOFF_DT], "%Y-%m-%d %H:%M:%S")
            distance = float(row[COL_DISTANCE])
            fare = float(row[COL_FARE])
            tip = float(row[COL_TIP])
        except (ValueError, IndexError):
            continue

        minutes = (dropoff - pickup).total_seconds() / 60.0
        if minutes <= 0 or minutes > 360:
            continue

        print(f"{bucket(minutes)}\t{fare},{distance},{tip},1")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
mapper_distance.py -- Analysis (f) Distance-Based Fare Analysis

KEY   = distance bucket: "0-2", "2-5", "5-10", "10-20", "20+"
VALUE = "fare_amount,trip_distance,1"

trip_distance <= 0 is skipped here (it is handled/reported separately
by the anomaly job) so that every row we bucket is a real, positive
distance.
"""
import sys
import csv

COL_DISTANCE = 4
COL_FARE = 10


def bucket(distance):
    if distance <= 2:
        return "0-2"
    if distance <= 5:
        return "2-5"
    if distance <= 10:
        return "5-10"
    if distance <= 20:
        return "10-20"
    return "20+"


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_FARE:
            continue
        try:
            int(row[0])
            distance = float(row[COL_DISTANCE])
            fare = float(row[COL_FARE])
        except (ValueError, IndexError):
            continue

        if distance <= 0:
            continue

        print(f"{bucket(distance)}\t{fare},{distance},1")


if __name__ == "__main__":
    main()

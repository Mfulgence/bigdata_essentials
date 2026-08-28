#!/usr/bin/env python3
"""
mapper_daily.py -- Analysis (b) Daily Demand (day of week)

KEY   = day name, "Mon".."Sun"
VALUE = 1

Weekday/weekend comparison is done later as post-processing on the tiny
7-row reducer output -- no need for a second MapReduce stage for that.
"""
import sys
import csv
from datetime import datetime

COL_PICKUP_DT = 1
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_PICKUP_DT:
            continue
        try:
            int(row[0])
            pickup = datetime.strptime(row[COL_PICKUP_DT], "%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            continue

        print(f"{DAY_NAMES[pickup.weekday()]}\t1")


if __name__ == "__main__":
    main()

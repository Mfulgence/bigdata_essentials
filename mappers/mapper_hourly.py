#!/usr/bin/env python3
"""
mapper_hourly.py -- Analysis (a) Hourly Taxi Demand

Hadoop Streaming feeds this script one line of the input CSV at a time on
stdin, and reads whatever it prints on stdout as the map output.

KEY   = pickup hour, "00".."23"   (what we want to group trips by)
VALUE = 1                          (one trip -- reducer will sum these)

Yellow taxi CSV columns (standard 2023/2024 schema -- run
`head -1 <file>` on your own file and adjust COL_PICKUP_DT below if your
column order differs):

0 VendorID | 1 tpep_pickup_datetime | 2 tpep_dropoff_datetime
3 passenger_count | 4 trip_distance | 5 RatecodeID | 6 store_and_fwd_flag
7 PULocationID | 8 DOLocationID | 9 payment_type | 10 fare_amount
11 extra | 12 mta_tax | 13 tip_amount | 14 tolls_amount
15 improvement_surcharge | 16 total_amount | 17 congestion_surcharge
18 airport_fee
"""
import sys
import csv
from datetime import datetime

COL_PICKUP_DT = 1


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_PICKUP_DT:
            continue
        try:
            # First column must be an integer VendorID -- this is how we
            # silently skip the header line and any malformed rows,
            # without needing to know which HDFS block/file we're in.
            int(row[0])
            pickup = datetime.strptime(row[COL_PICKUP_DT], "%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            continue

        print(f"{pickup.hour:02d}\t1")


if __name__ == "__main__":
    main()

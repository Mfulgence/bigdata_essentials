#!/usr/bin/env python3
"""
mapper_top_revenue.py -- JOB 2, stage 1 of the compulsory two-stage
MapReduce workflow.

Its INPUT is JOB 1's HDFS OUTPUT (/taxi_project/output/revenue/part-*),
not the raw taxi data. Each line there already looks like:
    PULocationID \t trip_count,total_fare,total_tip,total_revenue,avg_fare,avg_distance
(produced by reducers/reducer_revenue.py)

KEY   = "ALL"  (a constant -- see below)
VALUE = "PULocationID,total_revenue"

Why a constant key? Finding a global Top-N requires seeing every zone's
revenue *at once*, in one place, so they can be ranked against each
other. Hadoop only guarantees that identical keys land on the same
reducer -- so mapping every record to the same key is exactly how we
force all ~263 zones onto a single reducer for a global sort. This is
a well-known Hadoop Streaming trick for global Top-N, and it only works
because the result set (a few hundred zones) is small enough to fit in
one reducer's memory.
"""
import sys


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        try:
            pu_id, rest = line.split("\t", 1)
            total_revenue = rest.split(",")[3]
            float(total_revenue)
        except (ValueError, IndexError):
            continue

        print(f"ALL\t{pu_id},{total_revenue}")


if __name__ == "__main__":
    main()

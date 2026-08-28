#!/usr/bin/env python3
"""
reducer_top_revenue.py -- JOB 2, stage 2 of the compulsory two-stage
MapReduce workflow. Must be run with -numReduceTasks 1 (see
commands.txt) so exactly one reducer process receives every "ALL" line
and can sort them all together.

Input:  ALL \t PULocationID,total_revenue   (one line per zone)
Output: rank \t PULocationID \t total_revenue   (top 10 only)
"""
import sys

TOP_N = 10


def main():
    zones = []
    for line in sys.stdin:
        try:
            _, value = line.rstrip("\n").split("\t", 1)
            pu_id, revenue = value.split(",")
            zones.append((pu_id, float(revenue)))
        except ValueError:
            continue

    zones.sort(key=lambda pair: pair[1], reverse=True)

    for rank, (pu_id, revenue) in enumerate(zones[:TOP_N], start=1):
        print(f"{rank}\t{pu_id}\t{revenue:.2f}")


if __name__ == "__main__":
    main()

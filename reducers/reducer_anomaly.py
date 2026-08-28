#!/usr/bin/env python3
"""
reducer_anomaly.py -- pairs with mapper_anomaly.py
Output: anomaly_type \t flag_count

To turn this into "percentage of records affected" for the report,
divide each non-"normal" count by the total trip count from the
hourly job's output (sum of all hour counts) -- see WALKTHROUGH.md.
"""
import sys


def emit(key, count):
    if key is not None:
        print(f"{key}\t{count}")


def main():
    current_key = None
    current_count = 0

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t", 1)
            count = int(value)
        except ValueError:
            continue

        if key == current_key:
            current_count += count
        else:
            emit(current_key, current_count)
            current_key = key
            current_count = count

    emit(current_key, current_count)


if __name__ == "__main__":
    main()

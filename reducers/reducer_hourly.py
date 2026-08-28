#!/usr/bin/env python3
"""
reducer_hourly.py -- pairs with mapper_hourly.py

IMPORTANT for understanding Shuffle & Sort: Hadoop Streaming does NOT
hand the reducer a Python dict of {key: [values]} the way the native
Java API's Iterable<Text> does. It guarantees only that:
  1. all lines for the same key go to the same reducer, and
  2. those lines arrive sorted by key, so every key's lines are
     CONSECUTIVE on stdin.
That's why every reducer in this project follows the same manual
"track the current key, accumulate, flush when the key changes" loop
below -- it is the standard Hadoop Streaming reducer pattern.

Output: hour \t total_trips
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

#!/usr/bin/env python3
"""
reducer_daily.py -- pairs with mapper_daily.py
Output: day \t total_trips
(same sum-by-key pattern as reducer_hourly.py; see that file's comment
for why the loop is written this way)
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

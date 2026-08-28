#!/usr/bin/env python3
"""
reducer_location.py -- pairs with mapper_location.py
Output: PULocationID \t total_trips

Top-10 / Bottom-10 zones are found afterwards with a plain Unix sort
on this (small, ~263-row) output -- see commands.txt -- rather than a
second MapReduce stage, since the compulsory two-stage workflow is
already demonstrated by the revenue job (mapper_revenue.py ->
multistage/).
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

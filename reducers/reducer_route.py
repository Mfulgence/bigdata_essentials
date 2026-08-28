#!/usr/bin/env python3
"""
reducer_route.py -- pairs with mapper_route.py

Input value per line: "fare,total,1"
Output: PULocationID-DOLocationID \t trip_count,total_fare,total_revenue

Top-20 by count and Top-20 by revenue are both obtained by sorting this
one output on different columns locally (commands.txt) -- no need to
run the job twice.
"""
import sys


def flush(key, n, sum_fare, sum_total):
    if key is None or n == 0:
        return
    print(f"{key}\t{n},{sum_fare:.2f},{sum_total:.2f}")


def main():
    current_key = None
    n = sum_fare = sum_total = 0

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t", 1)
            fare, total, one = value.split(",")
            fare, total, one = float(fare), float(total), int(one)
        except ValueError:
            continue

        if key == current_key:
            n += one
            sum_fare += fare
            sum_total += total
        else:
            flush(current_key, n, sum_fare, sum_total)
            current_key = key
            n, sum_fare, sum_total = one, fare, total

    flush(current_key, n, sum_fare, sum_total)


if __name__ == "__main__":
    main()

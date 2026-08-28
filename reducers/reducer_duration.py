#!/usr/bin/env python3
"""
reducer_duration.py -- pairs with mapper_duration.py

Input value per line: "fare,distance,tip,1"
Output: duration_bucket \t trip_count,avg_fare,avg_distance,avg_tip
"""
import sys


def flush(key, n, sum_fare, sum_dist, sum_tip):
    if key is None or n == 0:
        return
    print(
        f"{key}\t{n},{sum_fare / n:.2f},{sum_dist / n:.2f},{sum_tip / n:.2f}"
    )


def main():
    current_key = None
    n = sum_fare = sum_dist = sum_tip = 0

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t", 1)
            fare, dist, tip, one = value.split(",")
            fare, dist, tip, one = float(fare), float(dist), float(tip), int(one)
        except ValueError:
            continue

        if key == current_key:
            n += one
            sum_fare += fare
            sum_dist += dist
            sum_tip += tip
        else:
            flush(current_key, n, sum_fare, sum_dist, sum_tip)
            current_key = key
            n, sum_fare, sum_dist, sum_tip = one, fare, dist, tip

    flush(current_key, n, sum_fare, sum_dist, sum_tip)


if __name__ == "__main__":
    main()

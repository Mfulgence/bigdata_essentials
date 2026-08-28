#!/usr/bin/env python3
"""
reducer_distance.py -- pairs with mapper_distance.py

Input value per line: "fare,distance,1"
Output: distance_bucket \t trip_count,total_fare,avg_fare,avg_distance,
                           avg_fare_per_mile
"""
import sys


def flush(key, n, sum_fare, sum_dist):
    if key is None or n == 0:
        return
    avg_fare = sum_fare / n
    avg_dist = sum_dist / n
    avg_fare_per_mile = sum_fare / sum_dist if sum_dist > 0 else 0
    print(
        f"{key}\t{n},{sum_fare:.2f},{avg_fare:.2f},{avg_dist:.2f},"
        f"{avg_fare_per_mile:.2f}"
    )


def main():
    current_key = None
    n = sum_fare = sum_dist = 0

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t", 1)
            fare, dist, one = value.split(",")
            fare, dist, one = float(fare), float(dist), int(one)
        except ValueError:
            continue

        if key == current_key:
            n += one
            sum_fare += fare
            sum_dist += dist
        else:
            flush(current_key, n, sum_fare, sum_dist)
            current_key = key
            n, sum_fare, sum_dist = one, fare, dist

    flush(current_key, n, sum_fare, sum_dist)


if __name__ == "__main__":
    main()

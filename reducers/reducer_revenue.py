#!/usr/bin/env python3
"""
reducer_revenue.py -- pairs with mapper_revenue.py (JOB 1 of the
compulsory two-stage workflow; JOB 2 lives in multistage/).

Input value per line: "fare,tip,total,distance,1"
Output: PULocationID \t trip_count,total_fare,total_tip,total_revenue,
                        avg_fare,avg_distance
"""
import sys


def flush(key, n, sum_fare, sum_tip, sum_total, sum_dist):
    if key is None or n == 0:
        return
    avg_fare = sum_fare / n
    avg_dist = sum_dist / n
    print(
        f"{key}\t{n},{sum_fare:.2f},{sum_tip:.2f},{sum_total:.2f},"
        f"{avg_fare:.2f},{avg_dist:.2f}"
    )


def main():
    current_key = None
    n = sum_fare = sum_tip = sum_total = sum_dist = 0

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t", 1)
            fare, tip, total, dist, one = value.split(",")
            fare, tip, total, dist, one = (
                float(fare), float(tip), float(total), float(dist), int(one)
            )
        except ValueError:
            continue

        if key == current_key:
            n += one
            sum_fare += fare
            sum_tip += tip
            sum_total += total
            sum_dist += dist
        else:
            flush(current_key, n, sum_fare, sum_tip, sum_total, sum_dist)
            current_key = key
            n, sum_fare, sum_tip, sum_total, sum_dist = one, fare, tip, total, dist

    flush(current_key, n, sum_fare, sum_tip, sum_total, sum_dist)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
reducer_payment.py -- pairs with mapper_payment.py

Input value per line: "fare,tip,total,1"
Output: payment_type \t trip_count,total_fare,total_tip,total_revenue,
                        avg_fare,avg_tip
"""
import sys


def flush(key, n, sum_fare, sum_tip, sum_total):
    if key is None or n == 0:
        return
    avg_fare = sum_fare / n
    avg_tip = sum_tip / n
    print(
        f"{key}\t{n},{sum_fare:.2f},{sum_tip:.2f},{sum_total:.2f},"
        f"{avg_fare:.2f},{avg_tip:.2f}"
    )


def main():
    current_key = None
    n = sum_fare = sum_tip = sum_total = 0

    for line in sys.stdin:
        try:
            key, value = line.rstrip("\n").split("\t", 1)
            fare, tip, total, one = value.split(",")
            fare, tip, total, one = float(fare), float(tip), float(total), int(one)
        except ValueError:
            continue

        if key == current_key:
            n += one
            sum_fare += fare
            sum_tip += tip
            sum_total += total
        else:
            flush(current_key, n, sum_fare, sum_tip, sum_total)
            current_key = key
            n, sum_fare, sum_tip, sum_total = one, fare, tip, total

    flush(current_key, n, sum_fare, sum_tip, sum_total)


if __name__ == "__main__":
    main()

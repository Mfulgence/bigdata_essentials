#!/usr/bin/env python3
"""
mapper_payment.py -- Analysis (e) Payment Method Analysis

KEY   = payment type name (Credit_card, Cash, No_charge, Dispute,
        Unknown, Voided_trip, Other)
VALUE = "fare_amount,tip_amount,total_amount,1"
"""
import sys
import csv

COL_PAYMENT_TYPE = 9
COL_FARE = 10
COL_TIP = 13
COL_TOTAL = 16

PAYMENT_NAMES = {
    1: "Credit_card",
    2: "Cash",
    3: "No_charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided_trip",
}


def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if len(row) <= COL_TOTAL:
            continue
        try:
            int(row[0])
            payment_code = int(row[COL_PAYMENT_TYPE])
            fare = float(row[COL_FARE])
            tip = float(row[COL_TIP])
            total = float(row[COL_TOTAL])
        except (ValueError, IndexError):
            continue

        name = PAYMENT_NAMES.get(payment_code, "Other")
        print(f"{name}\t{fare},{tip},{total},1")


if __name__ == "__main__":
    main()

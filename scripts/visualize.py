#!/usr/bin/env python3
"""
visualize.py -- Section 14, Required Visualizations

Reads the reducer outputs AFTER you have pulled them out of HDFS with
`hdfs dfs -getmerge` (see commands.txt) into a local `results/`
directory, using these fixed file names:

    results/hourly.tsv     hour, trip_count
    results/daily.tsv      day, trip_count
    results/location.tsv   PULocationID, trip_count
    results/payment.tsv    payment_type, trip_count, total_fare, total_tip,
                            total_revenue, avg_fare, avg_tip
    results/distance.tsv   bucket, trip_count, total_fare, avg_fare,
                            avg_distance, avg_fare_per_mile
    results/route.tsv      route, trip_count, total_fare, total_revenue

Zone IDs are labelled with names when data/taxi_zone_lookup.csv
(downloaded from the TLC site) is present; otherwise raw IDs are used.

Produces the 7 required charts as PNGs under reports/figures/.

Usage:
    python visualize.py [results_dir] [figures_dir]
"""
import sys
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DISTANCE_ORDER = ["0-2", "2-5", "5-10", "10-20", "20+"]


def load_zone_lookup(data_dir="data"):
    path = os.path.join(data_dir, "taxi_zone_lookup.csv")
    if os.path.exists(path):
        lookup = pd.read_csv(path)
        return dict(zip(lookup["LocationID"], lookup["Zone"]))
    return {}


def savefig(fig, out_dir, name):
    path = os.path.join(out_dir, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"wrote {path}")


def chart_hourly(results_dir, out_dir):
    df = pd.read_csv(os.path.join(results_dir, "hourly.tsv"), sep="\t",
                      names=["hour", "trips"])
    df = df.sort_values("hour")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["hour"].astype(str), df["trips"])
    ax.set_title("Trips by Hour of Day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Trip Count")
    savefig(fig, out_dir, "01_trips_by_hour.png")


def chart_daily(results_dir, out_dir):
    df = pd.read_csv(os.path.join(results_dir, "daily.tsv"), sep="\t",
                      names=["day", "trips"])
    df["day"] = pd.Categorical(df["day"], categories=DAY_ORDER, ordered=True)
    df = df.sort_values("day")
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#4C72B0"] * 5 + ["#DD8452"] * 2
    ax.bar(df["day"].astype(str), df["trips"], color=colors)
    ax.set_title("Trips by Day of Week (weekday vs weekend)")
    ax.set_ylabel("Trip Count")
    savefig(fig, out_dir, "02_trips_by_day_of_week.png")


def chart_top_locations(results_dir, out_dir, zone_names):
    df = pd.read_csv(os.path.join(results_dir, "location.tsv"), sep="\t",
                      names=["zone_id", "trips"])
    df = df.sort_values("trips", ascending=False).head(10)
    df["label"] = df["zone_id"].map(zone_names).fillna(df["zone_id"].astype(str))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df["label"][::-1], df["trips"][::-1])
    ax.set_title("Top 10 Pickup Zones by Trip Count")
    ax.set_xlabel("Trip Count")
    savefig(fig, out_dir, "03_top10_pickup_zones.png")


def chart_revenue_by_payment(results_dir, out_dir):
    df = pd.read_csv(
        os.path.join(results_dir, "payment.tsv"), sep="\t",
        names=["payment_type", "trips", "total_fare", "total_tip",
               "total_revenue", "avg_fare", "avg_tip"],
    )
    df = df.sort_values("total_revenue", ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["payment_type"], df["total_revenue"])
    ax.set_title("Total Revenue by Payment Method")
    ax.set_ylabel("Total Revenue ($)")
    savefig(fig, out_dir, "04_revenue_by_payment_method.png")


def chart_trips_by_distance(results_dir, out_dir):
    df = pd.read_csv(
        os.path.join(results_dir, "distance.tsv"), sep="\t",
        names=["bucket", "trips", "total_fare", "avg_fare", "avg_distance",
               "avg_fare_per_mile"],
    )
    df["bucket"] = pd.Categorical(df["bucket"], categories=DISTANCE_ORDER, ordered=True)
    df = df.sort_values("bucket")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["bucket"].astype(str), df["trips"])
    ax.set_title("Trips by Distance Category (miles)")
    ax.set_ylabel("Trip Count")
    savefig(fig, out_dir, "05_trips_by_distance_category.png")
    return df


def chart_top_routes(results_dir, out_dir, zone_names):
    df = pd.read_csv(
        os.path.join(results_dir, "route.tsv"), sep="\t",
        names=["route", "trips", "total_fare", "total_revenue"],
    )
    df = df.sort_values("trips", ascending=False).head(10)

    def label(route):
        pu, do = route.split("-")
        pu_name = zone_names.get(int(pu), pu)
        do_name = zone_names.get(int(do), do)
        return f"{pu_name} -> {do_name}"

    df["label"] = df["route"].apply(label)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(df["label"][::-1], df["trips"][::-1])
    ax.set_title("Top 10 Pickup-Dropoff Routes by Trip Count")
    ax.set_xlabel("Trip Count")
    savefig(fig, out_dir, "06_top10_routes.png")


def chart_revenue_vs_distance(distance_df, out_dir):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(distance_df["bucket"].astype(str), distance_df["avg_fare"], marker="o")
    ax.set_title("Average Fare vs Distance Category")
    ax.set_xlabel("Distance Category (miles)")
    ax.set_ylabel("Average Fare ($)")
    savefig(fig, out_dir, "07_revenue_vs_distance.png")


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "reports/figures"
    os.makedirs(out_dir, exist_ok=True)

    zone_names = load_zone_lookup()

    chart_hourly(results_dir, out_dir)
    chart_daily(results_dir, out_dir)
    chart_top_locations(results_dir, out_dir, zone_names)
    chart_revenue_by_payment(results_dir, out_dir)
    distance_df = chart_trips_by_distance(results_dir, out_dir)
    chart_top_routes(results_dir, out_dir, zone_names)
    chart_revenue_vs_distance(distance_df, out_dir)

    print("\nAll 7 required charts written to", out_dir)


if __name__ == "__main__":
    main()

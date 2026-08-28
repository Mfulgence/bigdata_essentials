#!/usr/bin/env python3
"""
pandas_baseline.py -- Section 12, Performance Comparison (compulsory)

Runs the SAME analysis as mapper_revenue.py / reducer_revenue.py
(revenue by pickup zone) but with plain single-machine Pandas, and
times/measures it, so it can be placed side-by-side with the Hadoop
MapReduce numbers pulled from the YARN application page.

Fill the "Hadoop MapReduce" column of the comparison table (Section 12
of the assignment) using:
  - Dataset Size / Number of Records: `hdfs dfs -du -h` and this
    script's own printed record count (same input file)
  - Execution Time: wall-clock time shown on the YARN application page
    (Started / Finished) for the SAME revenue job
  - Memory Used: "Total Memory Allocated" on the YARN app page
  - Mapper Tasks / Reducer Tasks: counters on the YARN app page
  - Output Size: `hdfs dfs -du -h /taxi_project/output/revenue`

Usage:
    python pandas_baseline.py data/cleaned/yellow_tripdata_2024-01.csv
"""
import sys
import time
import tracemalloc
import pandas as pd


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <cleaned.csv>")
        sys.exit(1)
    path = sys.argv[1]

    tracemalloc.start()
    start = time.perf_counter()

    df = pd.read_csv(
        path,
        usecols=["PULocationID", "fare_amount", "tip_amount", "total_amount", "trip_distance"],
    )
    result = df.groupby("PULocationID").agg(
        trip_count=("fare_amount", "count"),
        total_fare=("fare_amount", "sum"),
        total_tip=("tip_amount", "sum"),
        total_revenue=("total_amount", "sum"),
        avg_fare=("fare_amount", "mean"),
        avg_distance=("trip_distance", "mean"),
    ).sort_values("total_revenue", ascending=False)

    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(result.head(10))
    print("\n--- Pandas baseline metrics (revenue by pickup zone) ---")
    print(f"Input file:        {path}")
    print(f"Records processed: {len(df):,}")
    print(f"Execution time:    {elapsed:.2f} s")
    print(f"Peak memory used:  {peak / (1024 ** 2):.1f} MB")
    print(f"Zones in output:   {len(result)}")

    out_path = path.rsplit(".", 1)[0] + "_pandas_revenue.csv"
    result.to_csv(out_path)
    print(f"\nFull result written to {out_path}")


if __name__ == "__main__":
    main()

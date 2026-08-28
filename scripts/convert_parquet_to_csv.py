#!/usr/bin/env python3
"""
convert_parquet_to_csv.py -- Section 5, Dataset Preparation

TLC now distributes trip data as monthly Parquet files. Hadoop
Streaming reads plain text line-by-line, so we convert each monthly
Parquet file to CSV before it goes into HDFS.

Why Parquet for storage but CSV for this assignment:
  - Parquet is columnar, compressed, and stores a schema -- reading
    only the columns you need is fast and it takes far less disk space.
    That's why TLC and most production big-data systems use it.
  - CSV is row/line-oriented plain text -- exactly the format Hadoop
    Streaming's line-based protocol expects (each line -> one record
    fed to the mapper's stdin). It's larger on disk and slower to
    parse, but it's the simplest way to demonstrate streaming
    MapReduce without writing a Parquet reader in every mapper.
This trade-off (compact/columnar vs. simple/line-oriented) is worth
restating in the report's Dataset Description section.

Usage:
    python convert_parquet_to_csv.py yellow_tripdata_2024-01.parquet \
        data/raw/yellow_tripdata_2024-01.csv
"""
import sys
import pyarrow.parquet as pq
import csv


def convert(parquet_path, csv_path, batch_size=250_000):
    pf = pq.ParquetFile(parquet_path)
    total_rows = 0

    with open(csv_path, "w", newline="") as out_f:
        writer = None
        for batch in pf.iter_batches(batch_size=batch_size):
            table = batch.to_pandas()
            if writer is None:
                writer = csv.writer(out_f)
                writer.writerow(table.columns.tolist())
            for row in table.itertuples(index=False, name=None):
                writer.writerow(row)
            total_rows += len(table)
            print(f"  ...{total_rows:,} rows written", file=sys.stderr)

    print(f"Done: {parquet_path} -> {csv_path} ({total_rows:,} rows)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.parquet> <output.csv>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])

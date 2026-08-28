# bigdata_essentials -- NYC Taxi Hadoop MapReduce Analytics

A Hadoop HDFS + Python MapReduce (Hadoop Streaming) analytics pipeline
over NYC TLC Yellow Taxi trip records, built for the *Big Data Hadoop
MapReduce Taxi Analytics* assignment.

**Start here:** [`WALKTHROUGH.md`](WALKTHROUGH.md) is the full baby-steps
guide -- what to do, in order, and *why* each step exists, so you can
explain any part of it to the instructor. This README is the quick
reference once you already understand the pipeline.

## Environment assumptions

- A working Hadoop installation (HDFS + YARN) reachable via `hdfs` and
  `hadoop` on your `$PATH`, with `$HADOOP_HOME` set. This project was
  built assuming a pseudo-distributed single-node cluster, but nothing
  here is specific to that -- it runs the same on a multi-node cluster.
- `jps` shows `NameNode`, `DataNode`, `ResourceManager`, `NodeManager`
  running.
- YARN ResourceManager UI reachable at `http://localhost:8088/cluster`.
- Python 3 available both locally and on every node that runs a mapper
  or reducer task (Hadoop Streaming shells out to `python3`).
- Local Python packages: `pandas`, `pyarrow`, `matplotlib`
  (`pip install pandas pyarrow matplotlib`).

## Directory structure

```
mappers/       9 mapper scripts, one per analysis (a-i)
reducers/      9 matching reducer scripts
multistage/    JOB 2 of the compulsory two-stage workflow
               (consumes reducer_revenue.py's HDFS output)
scripts/       local (non-Hadoop) helper scripts:
                 convert_parquet_to_csv.py  Section 5 dataset prep
                 clean_data.py              Section 7 data cleaning
                 pandas_baseline.py         Section 12 perf comparison
                 visualize.py               Section 14 required charts
data/          local raw/cleaned CSVs and the zone lookup table
               (gitignored -- too large to commit; see WALKTHROUGH.md)
results/       local copies of reducer outputs, pulled from HDFS via
               `hdfs dfs -getmerge` (gitignored)
reports/       figures/ (generated charts) + your written report
commands.txt   every HDFS + Hadoop Streaming command, ready to copy-paste
```

## Quick execution order

1. Download 2-3 months of Yellow Taxi Parquet files from the
   [official TLC page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
   into `data/raw/`.
2. `python scripts/convert_parquet_to_csv.py <in>.parquet <out>.csv`
3. `python scripts/clean_data.py <raw>.csv <cleaned>.csv`
4. Upload raw + cleaned CSVs to HDFS (`commands.txt` section 3).
5. Run each of the 9 single-stage Hadoop Streaming jobs
   (`commands.txt` section 4).
6. Run the multi-stage top-revenue job (`commands.txt` section 5).
7. Capture YARN evidence at `http://localhost:8088/cluster`
   (`commands.txt` section 6).
8. `hdfs dfs -getmerge` every job's output into `results/`
   (`commands.txt` section 7).
9. `python scripts/pandas_baseline.py <cleaned>.csv` for the
   performance comparison table (`commands.txt` section 8).
10. `python scripts/visualize.py results reports/figures` for the 7
    required charts.
11. Write the report using the structure in Section 18 of the
    assignment brief, embedding the charts and screenshots with a
    short interpretation for each (screenshots without interpretation
    get limited credit -- see Section 16).

Full detail and reasoning for every one of these steps: see
[`WALKTHROUGH.md`](WALKTHROUGH.md).

## Testing a mapper/reducer pair locally (no Hadoop needed)

Before touching the cluster, always sanity-check a job on a small
local sample -- this is the fastest way to catch a bug (also explained
in WALKTHROUGH.md, Step 5):

```bash
head -50000 data/cleaned/yellow_tripdata_2024-01.csv > data/sample.csv
cat data/sample.csv | python3 mappers/mapper_hourly.py | sort | python3 reducers/reducer_hourly.py
```

This pipeline (`mapper | sort | reducer`) is exactly what Hadoop does
internally during Shuffle & Sort, just on one machine instead of
across a cluster.

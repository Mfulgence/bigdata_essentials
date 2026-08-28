# Baby-Steps Walkthrough

This is the complete, ordered path through the assignment. Each step
says **what to do**, **why it exists**, and **what you should be able
to explain** about it afterwards -- because the instructor can pick any
submitted program and ask you to justify its key-value design, its
Shuffle & Sort behavior, its reducer logic, and its result (Section 19,
Academic Integrity). Read a step's "why" before running its commands.

All commands referenced here are copy-paste-ready in `commands.txt`.

---

## Step 0 -- The mental model, before touching anything

Every job in this project is the same three-stage pipeline, run once
per analysis:

```
raw CSV lines  --MAP-->  (key, value) pairs
               --SHUFFLE & SORT--> Hadoop groups+sorts pairs by key,
                                    routes each key to one reducer
               --REDUCE-->  one summarized line per key
```

Hadoop Streaming's contract with your Python scripts is deliberately
dumb and language-agnostic: your mapper reads **lines of text** from
stdin and writes **`key\tvalue`** lines to stdout; your reducer reads
`key\tvalue` lines from stdin (already sorted and grouped by key by
Hadoop) and writes whatever final output line it wants. That's the
entire interface. There is no shared memory, no RPC, no framework
object model -- just text piped between processes, which is also
exactly what `mapper.py | sort | reducer.py` does on your laptop.
That equivalence is why Step 5 below (local testing) works at all, and
it's the cleanest way to explain Hadoop Streaming to an instructor.

Every mapper in `mappers/` picks one field (or a small combination) of
each trip to group by -- that's the analysis. Every reducer in
`reducers/` does the same thing: accumulate values for one key,
print a summary line when the key changes. Once you can explain *one*
mapper/reducer pair in depth, you can explain all nine, because they
share one pattern. `reducers/reducer_hourly.py` has the fullest
comment explaining that pattern -- read it first.

---

## Step 1 -- Confirm your Hadoop environment

```bash
jps
```

You should see `NameNode`, `DataNode`, `ResourceManager`,
`NodeManager` (and `SecondaryNameNode` on a pseudo-distributed setup).
If any are missing, start them (`start-dfs.sh`, `start-yarn.sh`) before
continuing -- nothing else in this guide works without HDFS and YARN
both up.

Open `http://localhost:8088/cluster` in a browser now, so you know it
resolves before you need it for Section 11 evidence later.

**Be ready to explain:** what each daemon does -- NameNode (HDFS
metadata/namespace), DataNode (stores actual data blocks),
ResourceManager (YARN's cluster-wide scheduler), NodeManager (runs
containers on one node).

---

## Step 2 -- Get the dataset (Section 2)

Go to the official TLC page:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Download **2-3 monthly Yellow Taxi Parquet files** (e.g.
`yellow_tripdata_2024-01.parquet`, `-02`, `-03`) into `data/raw/`. The
assignment lets you stop once you hit 2-3 months *or* 5 million
records, whichever comes first -- with 3 million+ trips/month for
Yellow Taxi, one month alone usually already clears 5 million, but use
2-3 months anyway so your Daily/Weekday-vs-Weekend analysis (b) has
enough spread of dates to be meaningful.

Also grab the zone lookup table (small CSV, maps `LocationID` to a
Borough/Zone name) into `data/taxi_zone_lookup.csv` -- used later to
label pickup zones and routes with real names instead of bare IDs in
your charts and report:
```
curl -o data/taxi_zone_lookup.csv \
  "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"
```

**Be ready to explain:** why TLC data specifically -- it's real,
public, large-scale operational data, which is exactly the shape of
data HDFS/MapReduce were built for (too big for one machine's RAM,
naturally splittable by month/row).

---

## Step 3 -- Convert Parquet to CSV (Section 5)

```bash
python scripts/convert_parquet_to_csv.py \
  data/raw/yellow_tripdata_2024-01.parquet \
  data/raw/yellow_tripdata_2024-01.csv
```

Repeat per month.

**Be ready to explain the trade-off** (this is a required discussion
point in the report, Section 5):
- **Parquet** is columnar and compressed with an embedded schema. TLC
  ships it because reading only the 3 columns you need out of 19 is
  fast, and file size is a fraction of CSV's. It's the right format
  for large-scale *storage*.
- **CSV** is plain text, one full record per line. Hadoop Streaming's
  protocol is line-oriented (it hands your mapper one line at a time
  on stdin) -- CSV lines up with that model directly, at the cost of
  being larger on disk and needing re-parsing on every read. It's the
  right format for *demonstrating line-oriented streaming*, which is
  the point of this assignment.

---

## Step 4 -- Clean the data (Section 7)

```bash
python scripts/clean_data.py \
  data/raw/yellow_tripdata_2024-01.csv \
  data/cleaned/yellow_tripdata_2024-01.csv
```

This drops only **hard-invalid** rows and tells you exactly how many
rows each rule removed (printed, and saved to
`*_cleaning_report.json`): missing required fields, unparseable
timestamps, `passenger_count <= 0`, `trip_distance <= 0`,
`fare_amount <= 0`, dropoff at or before pickup, trip duration over 6
hours, and exact duplicate rows. Read `scripts/clean_data.py`'s
docstring for the full rule list.

**Why this is split from Anomaly Detection (i):** Section 7 (cleaning)
and Section 8i (anomalies) sound similar but do different jobs on
purpose. Cleaning removes rows that **cannot** be real trips (negative
distance, zero fare) -- keeping them would corrupt every other
analysis's sums and averages, so removing them is safe and
justifiable. Anomaly Detection then runs on the *survivors* and flags
rows that are unusual but still *possible* (7 passengers, a
$60/mile fare) -- the assignment explicitly says not to delete those
without justification, so they're counted and categorized instead,
never dropped. This is exactly the distinction to state if asked "why
didn't you just delete the anomalies during cleaning?"

Record the `*_cleaning_report.json` numbers now -- you'll paste the
counts/percentages straight into the report's Data Cleaning section.

---

## Step 5 -- Test one mapper/reducer pair locally, before Hadoop

This is the single most useful debugging habit in this project. Do it
for every job before you ever run it on the cluster:

```bash
head -50000 data/cleaned/yellow_tripdata_2024-01.csv > data/sample.csv
cat data/sample.csv | python3 mappers/mapper_hourly.py | sort | python3 reducers/reducer_hourly.py
```

If this produces 24 lines (`00` through `23`, tab-separated from a
count) that look sane, the job's logic is correct -- any failure on
the actual cluster from here on is an infrastructure/command problem,
not a logic bug, which is a huge time-saver when debugging.

`sort` here is standing in for Hadoop's Shuffle & Sort phase: it's the
same operation (group and order by the text before the first tab),
just running on one machine, single-threaded, instead of distributed
across the cluster with a partitioner deciding which reducer each key
goes to. Being able to say that sentence is worth rehearsing --
"Shuffle and Sort" is explicitly named in the learning objectives.

Repeat this for the other 8 mapper/reducer pairs (and the multi-stage
pair in `multistage/`, once you have Job 1's real output to feed it).

---

## Step 6 -- Create the HDFS directory structure (Section 6)

Run the `mkdir -p` and `rmdir` block in `commands.txt` section 1.

**Why the `rmdir` after `mkdir -p`:** Hadoop Streaming refuses to run
if `-output` already exists (it always creates that directory itself,
so a leftover one looks like a name collision / risk of overwriting
old results). We pre-create the *parent* `/taxi_project/output/`
tree for a tidy `hdfs dfs -ls`, then remove the specific job output
directories so each `hadoop jar ... -output ...` call can create its
own from scratch. If you re-run a job later, `hdfs dfs -rm -r` its
output directory first.

**Be ready to explain the structure itself:** `input/raw` (as
downloaded/converted, unmodified), `input/cleaned` (what every
MapReduce job actually reads), `output/<analysis>` (one directory per
job, holding `part-00000`, `part-00001`, ... reducer output files),
`archive/` (raw files moved aside once cleaned data is verified, so
`input/raw` doesn't linger forever).

---

## Step 7 -- Upload to HDFS

Run `commands.txt` section 3: `hdfs dfs -put` both raw and cleaned
CSVs, then `-ls -h`, `-du -h`, and `hdfs dfsadmin -report`.

**Be ready to explain:** `-ls -h` shows file sizes and replication
factor; `-du -h` shows aggregate directory size; `dfsadmin -report`
shows cluster-wide capacity/usage per DataNode. Also know the default
HDFS block size (128 MB) and that `hdfs fsck <path> -files -blocks`
will show you exactly how a large CSV got split into blocks across
the cluster -- that's the concrete, inspectable version of "HDFS
stores large datasets across a distributed filesystem" from the
assignment brief.

---

## Step 8 -- Anatomy of a Hadoop Streaming command

Every job in `commands.txt` section 4 has the same shape:

```bash
hadoop jar $STREAM_JAR \
  -input /taxi_project/input/cleaned \
  -output /taxi_project/output/hourly \
  -mapper "python3 mapper_hourly.py" \
  -reducer "python3 reducer_hourly.py" \
  -file mappers/mapper_hourly.py \
  -file reducers/reducer_hourly.py
```

- `$STREAM_JAR` -- the generic Hadoop Streaming jar; it doesn't know
  anything about taxis, it just wires stdin/stdout of arbitrary
  external programs into the Map and Reduce phases.
- `-input` / `-output` -- HDFS paths, not local paths.
- `-mapper` / `-reducer` -- the shell command each map/reduce task
  runs. It's `"python3 mapper_hourly.py"`, not a path, because...
- `-file` -- ships that local file to every node that runs a task for
  this job, placing it in the task's working directory -- which is
  *why* `-mapper "python3 mapper_hourly.py"` (a bare filename) works
  even on a multi-node cluster where the script was never manually
  copied to each machine.

Run each of the 9 single-stage jobs from `commands.txt` section 4 now,
one at a time. After each one, spot-check its output:
```bash
hdfs dfs -cat /taxi_project/output/hourly/part-* | head
```

**Per-job key-value design you should be able to state from memory**
(each mapper file's own docstring has the full reasoning):

| Job | Mapper key | Mapper value |
|---|---|---|
| a) hourly | pickup hour `"00"`-`"23"` | `1` |
| b) daily | day name `"Mon"`-`"Sun"` | `1` |
| c) locations | `PULocationID` | `1` |
| d) revenue | `PULocationID` | `fare,tip,total,distance,1` |
| e) payment | payment type name | `fare,tip,total,1` |
| f) distance | distance bucket | `fare,distance,1` |
| g) routes | `"PULocationID-DOLocationID"` | `fare,total,1` |
| h) duration | duration bucket | `fare,distance,tip,1` |
| i) anomalies | anomaly type name | `1` |

Every reducer follows the pattern in Step 0 -- accumulate while the
key matches, flush and reset when it changes.

---

## Step 9 -- Multi-stage MapReduce (Section 9, compulsory)

Run `commands.txt` section 5.

Job 1 is just the Revenue-by-Pickup-Location job you already ran in
Step 8 (`mapper_revenue.py` / `reducer_revenue.py`) -- its HDFS output
at `/taxi_project/output/revenue/` **is** the input to Job 2. Look at
it directly (`hdfs dfs -cat ... | head`) before running Job 2 -- that
`cat` output is your "show the intermediate HDFS output" evidence.

Job 2 (`multistage/mapper_top_revenue.py` +
`multistage/reducer_top_revenue.py`) finds the global top-10
highest-revenue zones. The one nonobvious trick, worth rehearsing for
the instructor: **the mapper emits a constant key, `"ALL"`, for every
line.** Hadoop's only real guarantee is "same key -> same reducer" --
there is no separate "give me everything, globally sorted" primitive
in the streaming model. So forcing every record to share one key is
how you force all ~263 zones' totals onto a single reducer process,
where a plain Python `sort()` on the whole in-memory list gives you a
true global ranking. This only scales because the *result* of Job 1
(one row per zone, a few hundred rows) is small, even though the
*input* to Job 1 (millions of trips) was not -- that distinction is
the crux of the "why multi-stage" design question.

`-D mapreduce.job.reduces=1` in the command pins this job to exactly
one reducer, so you don't get several separate `"ALL"` groups split
across parallel reducers by chance (a constant key already forces this
in practice via the partitioner, but setting it explicitly documents
the intent and is worth mentioning when asked).

---

## Step 10 -- YARN evidence (Section 11)

While a job is running (or from the History Server after it
finishes), open `http://localhost:8088/cluster`. For at least one job
(ideally the revenue job, since you'll reuse its numbers in Step 12),
screenshot and record:
- Application ID
- State / Final Status
- Start Time / Finish Time (-> execution time for Step 12)
- Number of Mapper and Reducer tasks/containers

**Be ready to explain:** YARN separates *resource management*
(ResourceManager + NodeManagers, deciding which node runs which
container) from *job execution* (the ApplicationMaster for your
specific MapReduce job, spawned inside a container, which then
requests more containers for your map and reduce tasks). This is the
architectural split that lets a YARN cluster run more than just
MapReduce (Spark, Tez, etc. all run as YARN applications too) --
useful if asked "why is it YARN and not just MapReduce running this."

---

## Step 11 -- Pull results locally and compute Top/Bottom-N

Run `commands.txt` section 7. `hdfs dfs -getmerge` concatenates every
`part-NNNNN` reducer output file for a job into one local file --
necessary because a job with multiple reducers writes multiple output
files, and you want one flat list to sort/chart.

Top-10/Bottom-10 pickup zones (c) and Top-20 routes by count and by
revenue (g) are then just a Unix `sort` on that small local file (a
few hundred to a few thousand lines) -- see the `sort`/`awk` one-liners
in `commands.txt`. **This is deliberately not a second MapReduce job:**
the compulsory two-stage requirement is already satisfied by Step 9,
and running MapReduce again over an output that's already small enough
to sort instantly on a laptop would be solving a distributed-systems
problem that no longer exists at that data size. Knowing when *not* to
reach for MapReduce is itself part of "understanding Hadoop MapReduce
design," so this is a legitimate point to make in the report, not a
shortcut you need to hide.

---

## Step 12 -- Performance comparison (Section 12, compulsory)

```bash
python scripts/pandas_baseline.py data/cleaned/yellow_tripdata_2024-01.csv
```

This runs the identical Revenue-by-Pickup-Location aggregation with
plain Pandas on one machine, timed and memory-profiled. Fill in the
comparison table (template in `commands.txt` section 8 and Section 12
of the assignment) using this script's printed numbers for the Pandas
column, and the Step 10 YARN numbers for the same `revenue` job for
the Hadoop column.

**Be ready to explain the result, whichever way it comes out:** on a
single month's data on a single-node pseudo-cluster, Pandas will very
likely be *faster* -- MapReduce has fixed overhead (JVM startup per
task, writing intermediate data to disk between Map and Reduce,
shuffling data across the network) that dominates at small scale.
Pandas holds everything in one process's RAM with no serialization or
network cost. The report should state this plainly and explain why
that flips as data grows past what fits in one machine's memory: at
that point Pandas simply cannot run at all (out of memory), while
Hadoop's overhead is amortized across many nodes working in parallel.
That crossover point -- not "Hadoop is always faster" -- is the actual
lesson Section 12 and business question (l) are testing.

---

## Step 13 -- Generate the 7 required charts (Section 14)

```bash
python scripts/visualize.py results reports/figures
```

Produces all 7 required charts as PNGs: trips by hour, trips by day
of week, top 10 pickup zones, revenue by payment method, trips by
distance category, top 10 routes, and average fare vs distance
category. Each one reads directly from the `results/*.tsv` files you
made in Step 11 -- open `scripts/visualize.py` and match each chart
function to the reducer output file it reads, so you can explain where
every number on every chart came from.

---

## Step 14 -- Answer the Final Business Questions (Section 15)

Every question a)-k) has a direct one-line answer sitting in one of
your `results/*.tsv` files or `*_cleaning_report.json` -- answer them
from your own numbers, not in the abstract:

| Question | Where the answer comes from |
|---|---|
| a) busiest hour | top row of sorted `results/hourly.tsv` |
| b) busiest day | top row of sorted `results/daily.tsv` |
| c) top trip-count zones | `results/location.tsv`, sorted (Step 11) |
| d) top revenue zones | `results/top_revenue.tsv` (Step 9) |
| e) payment method driving most revenue | `results/payment.tsv`, `total_revenue` column |
| f) do credit-card users tip more | compare `avg_tip` for `Credit_card` vs `Cash` in `results/payment.tsv` |
| g) distance category with highest avg fare | `results/distance.tsv`, `avg_fare` column |
| h) most frequent routes | `results/route.tsv` sorted by trip count (Step 11) |
| i) frequent vs. profitable routes | compare that ranking against the same file sorted by `total_revenue` |
| j) % records with anomalies | `results/anomaly.tsv` counts / total trips from `results/hourly.tsv` summed |
| k) business insights | your own synthesis across all of the above |

Question (l) -- "when does Hadoop MapReduce provide a meaningful
advantage" -- is answered by Step 12's crossover-point discussion, not
by a number.

---

## Step 15 -- Write the report (Sections 16-18)

Follow the Section 18 structure directly; it maps almost one-to-one
onto the steps above:

- **Dataset Description / Hadoop Environment / HDFS Design** <- Steps 1-2, 6-7
- **Data Cleaning** <- Step 4's `*_cleaning_report.json` numbers
- **MapReduce Design / Mapper and Reducer Implementation** <- Step 8's
  table, plus each mapper/reducer file's docstring
- **Analytical Results** <- Steps 11-14's numbers and charts
- **Multi-Stage MapReduce** <- Step 9
- **YARN Analysis** <- Step 10's screenshots, captioned with what each
  field means (Section 16: screenshots need interpretation, not just a
  picture)
- **Performance Comparison** <- Step 12
- **Business Insights / Limitations / Conclusion** <- Step 14's
  answers plus your own judgment (e.g. limitations: single-node
  pseudo-cluster scale, months chosen, cleaning thresholds chosen)

Every screenshot from Section 16's checklist should have 1-3 sentences
under it saying what it shows and why it matters -- that's a scoring
requirement, not decoration.

---

## Step 16 -- Before the demo: rehearse being asked about ANY file

Section 19 means the instructor may point at, say,
`reducers/reducer_route.py` cold and ask you to walk through it. For
every mapper/reducer pair, be able to answer, without notes:

1. What is the key, and why that field (or combination)?
2. What is the value, and why pack those specific numbers into it?
3. What does Shuffle & Sort guarantee happens to these key-value pairs
   before the reducer sees them?
4. Walk through the reducer's accumulate/flush loop on a tiny made-up
   example (3-4 lines of input) and say what it prints.
5. What does the final HDFS output mean, in one sentence, and how did
   you use it in the report/business questions?

If you can do that for `reducer_hourly.py` (the simplest) and
`reducer_revenue.py` (the multi-field one) plus the `multistage/`
pair, the rest all follow the identical pattern with different fields
-- which is itself a fine thing to say out loud in the demo.

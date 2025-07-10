# NYC Taxi Data Pipeline README

## Overview

This project builds an end-to-end data pipeline for NYC taxi trip data. It downloads Parquet files, converts them to CSV, stages them in Google Cloud Storage, processes and transforms them with Cloud Data Fusion (using Wrangler), loads the results into BigQuery, then creates derived tables for analytics.

---

## Tech Stack

| Layer                   | Technology                        | Version / Plugins                         |
|-------------------------|-----------------------------------|--------------------------------------------|
| Extraction & Staging    | Python                            | 3.8+                                       |
|                         | requests                          | 2.28+                                      |
|                         | pandas                            | 1.5+                                       |
|                         | pyarrow                           | 11.0+                                      |
|                         | google-cloud-storage              | 2.10+                                      |
| Data Orchestration      | Google Cloud Data Fusion (CDAP)   | 6.x                                        |
|                         | Wrangler plugin                   | Built-in                                   |
|                         | GCSFile Source                    | Built-in                                   |
|                         | BigQuery Sink                     | Built-in                                   |
| Data Warehouse          | Google BigQuery                   | n/a                                        |
| BI & Visualization      | Power BI Desktop                  | 2.115+ (Google BigQuery connector enabled) |

---

## Screenshots

Place your exported pipeline and UI screenshots under a `screenshots/` folder and reference them here:

| Filename                                   | Description                                           |
|--------------------------------------------|-------------------------------------------------------|
| `01-csv-parse-options.png`                 | CSV Parsing Options in GCSFile source                 |
| `02-pipeline-overview.png`                 | ETLpipeliner flow: GCSFile → Wrangler → BigQuery      |
| `03-wrangler-recipe.png`                   | Wrangler recipe steps                                 |
| `04-bq-sink-config.png`                    | BigQuery sink configuration in Cloud Data Fusion      |
| `05-bq-sql-hourly-stats.png`               | BigQuery SQL: Hourly trip statistics                  |
| `06-bq-sql-daily-summary.png`              | BigQuery SQL: Daily revenue & trip volume             |
| `07-bq-sql-zone-performance.png`           | BigQuery SQL: Pickup zone performance                 |
| `08-bq-sql-tip-percentage.png`             | BigQuery SQL: Tip percentage distribution             |
| `09-powerbi-get-data.png`                  | Power BI “Get Data → Google BigQuery” dialog          |
| `10-powerbi-navigator.png`                 | Power BI Navigator selecting tables                   |
| `11-powerbi-report.png`                    | Final Power BI visualization (charts & map)           |

---

## 1. Data Extraction (`extract.py`)

We download a publicly hosted Parquet file, convert it to CSV, and upload to GCS.

2. Cloud Data Fusion Pipeline
Pipeline name: ETLpipeliner Flow: GCSFile → Wrangler → BigQuery
2.2 Wrangler Transform

Applied recipe steps:

Step	Transformation	Details
1	rename-column	tpep_pickup_datetime → pickup_datetime
tpep_dropoff_datetime → dropoff_datetime
2	set-type	passenger_count → INTEGER
trip_distance → FLOAT
3	drop-columns	payment_type, extra, mta_tax
4	filter-rows	Exclude if trip_distance ≤ 0 or fare_amount < 0
2.3 BigQuery Sink

Project: my-etlproject

Dataset: employee

Table: yellow_tripdata_2023_jan

Write disposition: WRITE_TRUNCATE

3. BigQuery Data Processing
3.1 Hourly Trip Statistics

sql
CREATE TABLE `my-etlproject.employee.taxi_hourly_stats` AS
SELECT
  EXTRACT(HOUR FROM tpep_pickup_datetime) AS trip_hour,
  COUNT(*)                                   AS trip_count,
  ROUND(AVG(trip_distance), 2)               AS avg_distance_miles,
  ROUND(SUM(total_amount), 2)                AS total_revenue_usd
FROM `my-etlproject.employee.yellow_tripdata_2023_jan`
GROUP BY trip_hour
ORDER BY trip_hour;
trip_hour: 0–23

trip_count: number of trips per hour

avg_distance_miles: average distance

total_revenue_usd: sum of total_amount

3.2 Daily Revenue and Trip Volume

sql
CREATE TABLE `my-etlproject.employee.taxi_daily_summary` AS
SELECT
  DATE(tpep_pickup_datetime)  AS trip_date,
  COUNT(*)                    AS total_trips,
  ROUND(SUM(fare_amount), 2)  AS total_fare_usd,
  ROUND(SUM(tip_amount), 2)   AS total_tips_usd
FROM `my-etlproject.employee.yellow_tripdata_2023_jan`
GROUP BY trip_date
ORDER BY trip_date;
trip_date: calendar date

total_trips: number of trips that day

total_fare_usd: sum of base fares

total_tips_usd: sum of tips

3.3 Pickup Zone Performance

sql
CREATE TABLE `my-etlproject.employee.taxi_zone_performance` AS
SELECT
  PULocationID                          AS pickup_zone_id,
  COUNT(*)                              AS trips_from_zone,
  ROUND(AVG(total_amount), 2)          AS avg_total_amount_usd
FROM `my-etlproject.employee.yellow_tripdata_2023_jan`
GROUP BY pickup_zone_id
ORDER BY trips_from_zone DESC
LIMIT 50;
pickup_zone_id: numeric pickup location

trips_from_zone: count of pickups

avg_total_amount_usd: average total amount

3.4 Tip Percentage Distribution

sql
CREATE TABLE `my-etlproject.employee.tip_percentage_distribution` AS
SELECT
  CASE
    WHEN tip_amount/NULLIF(total_amount,0) < 0.10 THEN '<10%'
    WHEN tip_amount/total_amount BETWEEN 0.10 AND 0.19 THEN '10–19%'
    WHEN tip_amount/total_amount BETWEEN 0.20 AND 0.29 THEN '20–29%'
    ELSE '30%+' END               AS tip_bucket,
  COUNT(*)                      AS trip_count,
  ROUND(AVG(tip_amount/total_amount)*100, 1) AS avg_tip_pct
FROM `my-etlproject.employee.yellow_tripdata_2023_jan`
GROUP BY tip_bucket
ORDER BY avg_tip_pct DESC;
tip_bucket: percentage range

trip_count: number of trips in bucket

avg_tip_pct: average tip percent

4. Power BI Visualization
4.1 Connect to BigQuery

Get Data → Google BigQuery

Choose project (my-etlproject) and dataset (employee)

Select each table (e.g., taxi_hourly_stats, taxi_daily_summary) and click Load

4.2 Navigator & Load

Tick the tables you want, then load into Power Query for optional shaping.

4.3 Final Report

1.Ratio of Hours to trips completed 

2.Revenue breakdown

3.Miles to Trip profit overall the companies lifecycle

4.Highest annula active trips

5.Average trips to tips ratio

6.Table of total trips to each zone ID's

<img width="592" height="332" alt="image" src="https://github.com/user-attachments/assets/84de33e2-87e0-433c-8ee8-bd62aa332919" />

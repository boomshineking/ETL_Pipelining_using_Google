import requests
import pandas as pd
from google.cloud import storage

# Step 1: Download the Parquet file
def download_parquet(url, local_parquet_file):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_parquet_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded Parquet file to {local_parquet_file}")

# Step 2: Convert Parquet to CSV
def convert_parquet_to_csv(parquet_file, csv_file):
    df = pd.read_parquet(parquet_file)
    df.to_csv(csv_file, index=False)
    print(f"Converted {parquet_file} to CSV and saved as {csv_file}")

# Step 3: Upload CSV to Google Cloud Storage
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f'Uploaded {source_file_name} to {destination_blob_name} in {bucket_name}')

# File and bucket details
parquet_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
parquet_local = "yellow_tripdata_2023-01.parquet"
csv_local = "yellow_tripdata_2023-01.csv"
bucket_name = "bkt-employee-data"
destination_blob_name = "yellow_tripdata_2023-01.csv"

# Run all steps
download_parquet(parquet_url, parquet_local)
convert_parquet_to_csv(parquet_local, csv_local)
upload_to_gcs(bucket_name, csv_local, destination_blob_name)

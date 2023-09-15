import boto3
import os
import glob
import pandas as pd


def parquet_to_s3(parquet_file, bucket_name, s3_key):
    # Load the parquet file
    data = pd.read_parquet(parquet_file)
    data.reset_index(inplace=True)

    # Convert the data to CSV

    json_file = "temp.csv"
    json_data = data.to_json(json_file, orient="values")

    # Upload the CSV file to S3
    s3 = boto3.client("s3")
    print("Uploading file ", s3_key, " to s3")
    s3.upload_file(json_file, bucket_name, s3_key)

    # Delete the local CSV file
    os.remove(json_file)


def replace_extension(filename, new_extension):
    base_name = os.path.splitext(filename)[0]
    return f"{base_name}.{new_extension}"


# ======================================================================================== #
#                                     MAIN CODE PART
# ======================================================================================== #
BUCKET_NAME = "rocketbot-tradingdata"


def upload_files_to_s3():
    # Get all Parquet files in the directory
    file_pattern = "data/*.parquet"
    parquet_files = glob.glob(file_pattern)
    # Load and append all Parquet files
    for file in parquet_files:
        parquet_to_s3(file, BUCKET_NAME, f"{replace_extension(file, 'json')}")


# upload_files_to_s3()

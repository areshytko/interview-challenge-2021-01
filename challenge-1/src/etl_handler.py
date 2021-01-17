"""
Entrypoint for AWS Lambda
"""

import os

import boto3

from challenge1.etl import preprocess


def lambda_handler(event, context):
    """Entrypoint for AWS Lambda 

    Expected event schema:
    {
        "bucket": str, # bucket with source raw data
        "key": str, # key of the object with source raw data
        "year": int # year of the source raw data
    }

    Also requires the following environment variables:
    - DEST_BUCKET - bucket for datamarts preprocessing results
    - DATAMART_KEY_PREFIX - prefix for the name of the datamart
    """

    # @TODO get dataset uuid and read its bucket and key from metadata service instead of this
    bucket, obj = event["bucket"], event["key"]

    dest_bucket = os.environ['DEST_BUCKET']
    obj_prefix = os.environ['DATAMART_KEY_PREFIX']
    year = event["year"]
    dest_obj = f"{obj_prefix}{year}"
    source_file = f'/tmp/{obj}'
    dest_file = f'/tmp/{dest_obj}'

    s3 = boto3.client('s3')
    s3.download_file(bucket, obj, source_file)

    preprocess(input_path=source_file, output_path=dest_file)

    # @TODO add proper logging

    s3.upload_file(
        Bucket=dest_bucket,
        Key=dest_obj,
        Filename=dest_file
    )

    # @TODO upload dataset metadata to a metadata service

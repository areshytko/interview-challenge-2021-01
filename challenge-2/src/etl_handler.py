"""
Entrypoint for AWS Lambda
"""

import os

import boto3

from challenge2.etl import load_dynamodb, preprocess


def lambda_handler(event, context):
    """
    Entrypoint for AWS Lambda 

    Expected event schema:
    {
        "bucket": str, # bucket with source raw data
        "key": str, # key of the object with source raw data
    }

    Also requires the following environment variables:
    - DEST_TABLE - DynamoDB table to store results
    - IMAGE_SIZE - the result width of the imager
    """

    bucket, well = event["bucket"], event["key"]
    dest_table = os.environ['DEST_TABLE']
    image_size = int(os.environ['IMAGE_SIZE'])
    source_file = f'/tmp/{well}'

    s3 = boto3.client('s3')
    s3.download_file(bucket, well, source_file)

    depth, img = preprocess(input_path=source_file, image_size=image_size)

    load_dynamodb(depth=depth, img=img, well=well, table=dest_table)

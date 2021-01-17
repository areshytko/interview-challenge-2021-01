"""
"""

import os

import boto3

from challenge2.etl import load_dynamodb, preprocess


def lambda_handler(event, context):

    bucket, well = event["bucket"], event["key"]
    dest_table = os.environ['DEST_TABLE']
    image_size = int(os.environ['IMAGE_SIZE'])
    source_file = f'/tmp/{well}'

    s3 = boto3.client('s3')
    s3.download_file(bucket, well, source_file)

    depth, img = preprocess(input_path=source_file, image_size=image_size)

    load_dynamodb(depth=depth, img=img, well=well, table=dest_table)

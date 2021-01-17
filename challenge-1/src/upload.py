#!/usr/bin/env python3
"""
CLI for uploading raw data to AWS S3 Data Lake
"""

import boto3
import click

from challenge1.etl import filter_invalid, read_raw_data


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--bucket', '-b', type=str, required=True, help="bucket to store the data to")
@click.option('--key', '-k', type=str, required=True, help="object key to store the data to")
@click.option('--dryrun', is_flag=True, help="provide just data validation and stats without upload")
def main(filename: str, bucket: str, key: str, dryrun: bool = False):

    data = read_raw_data(filename)

    if dryrun:
        print(data.df.describe())
        filtered_data = filter_invalid(data).df
        print(f"{len(data.df) - len(filtered_data)} rows of invalid data will be ignored")
    else:
        s3 = boto3.client('s3')
        s3.upload_file(
            Bucket=bucket,
            Key=key,
            Filename=filename
        )

        # @TODO upload dataset metadata to a metadata service


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter

"""
preprocessing functionality
"""

from typing import Tuple

import boto3
import numpy as np
import pandas as pd
from boto3.dynamodb.types import Binary
from PIL import Image

from challenge2.data import RawImagerData


def preprocess(input_path: str, image_size: int) -> Tuple[pd.Series, np.ndarray]:
    """
    Preprocss imager data into a depth, image tuple.
    Image is resized to a given width.
    Additionally, to avoid floating point difficulties, depth measurements are converted 
    to centimeters and integer type.

    Parameters
    ----------
    input_path : str
        path to an imager file in a RawImagerData format
    image_size : int
        resulted image width

    Returns
    -------
    Tuple[pd.Series, np.ndarray]
        depth measurements, image
    """
    data = pd.read_csv(input_path, **RawImagerData.STORAGE_FORMAT['read_params'])
    data = data.dropna()
    data = RawImagerData.convert(data)
    img = Image.fromarray(data.df.iloc[:, 1:].values)
    resized_img = img.resize((image_size, img.size[1]))
    result_img = np.asarray(resized_img)

    depth = (data.df.depth * 10**RawImagerData.DEPTH_PRECISION_DIGITS).astype(np.int64)

    return depth, result_img


def load_dynamodb(depth: pd.Series, img: np.ndarray, well: str, table: str):
    """
    Load image data into DynamoDB table

    Parameters
    ----------
    depth : pd.Series
        depth measurements
    img : np.ndarray
        imager
    well : str
        well id
    table : str
        DynamoDB table name
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)

    with table.batch_writer() as batch:
        for i, (depth_val, image_row) in enumerate(zip(depth, img)):
            if i % 100 == 0:
                print(f"Processed {i} items")
            batch.put_item(
                Item={
                    'well': well,
                    'depth': depth_val,
                    'image': Binary(image_row.tostring())
                }
            )

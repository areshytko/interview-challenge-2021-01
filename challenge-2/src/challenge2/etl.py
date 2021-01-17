"""
"""

from typing import Tuple

import boto3
import numpy as np
import pandas as pd
from boto3.dynamodb.types import Binary
from PIL import Image

from challenge2.data import RawImagerData


def preprocess(input_path: str, image_size: int) -> Tuple[pd.Series, np.ndarray]:
    data = pd.read_csv(input_path, **RawImagerData.STORAGE_FORMAT['read_params'])
    data = data.dropna()
    data = RawImagerData.convert(data)
    img = Image.fromarray(data.df.iloc[:, 1:].values)
    resized_img = img.resize((image_size, img.size[1]))
    result_img = np.asarray(resized_img)

    depth = (data.df.depth * 10**RawImagerData.DEPTH_PRECISION_DIGITS).astype(np.int64)

    return depth, result_img


def load_dynamodb(depth: pd.Series, img: np.ndarray, well: str, table: str):
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

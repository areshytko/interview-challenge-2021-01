"""
data querying functionality
"""

from typing import Optional

import boto3
import numpy as np
from boto3.dynamodb.conditions import Key
from matplotlib import cm


def minmax_normalize(data: np.ndarray) -> np.ndarray:
    """
    minmax normalizaion of numpy array
    """
    minval, maxval = np.min(data), np.max(data)
    if minval == maxval:
        norm_data = data * 0
    else:
        norm_data = (data - minval) / (maxval - minval)
    return norm_data


def apply_colormap(img: np.ndarray, colormap: str) -> np.ndarray:
    """
    Apply color man to image array.

    Parameters
    ----------
    img : np.ndarray
    colormap : str
        name of colormap from `matplotlib.cm` package
    """
    img = minmax_normalize(img)
    colormap = getattr(cm, colormap)
    result = np.uint8(colormap(img)*255)
    return result


def query_imager(well_id: str,
                 imager_table: str,
                 min_depth: float,
                 max_depth: float,
                 colormap: Optional[str] = None,
                 region_name: Optional[str] = None) -> np.ndarray:
    """
    Query imager data by well id and depth range from DynamoDB table.

    Parameters
    ----------
    well_id : str
    imager_table : str
    min_depth : float
    max_depth : float
    colormap : Optional[str], optional
        name of colormap from `matplotlib.cm` package, by default None
    region_name : Optional[str], optional
        AWS region_name for DynamoDB table, by default None

    Returns
    -------
    np.ndarray
        imager slice for the well, if none is found, empty array is returned
    """

    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(imager_table)

    min_depth = round(min_depth * 10)
    max_depth = round(max_depth * 10)

    response = table.query(
        KeyConditionExpression=Key('depth').between(min_depth, max_depth) & Key('well').eq(well_id)
    )
    items = response['Items']

    if len(items) == 0:
        return np.ndarray(shape=(0, 0))

    images = (x['image'] for x in items)
    image = np.stack([np.frombuffer(x.value, dtype=np.uint8) for x in images])
    if colormap:
        image = apply_colormap(img=image, colormap=colormap)
    return image

"""
Web service main file to API access of well imager slices.
"""

import os
from typing import List, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from challenge2.select import query_imager

app = FastAPI()


class ImagerModel(BaseModel):
    """
    GET: /imagers result schema
    """
    well_id: str
    min_depth: float
    max_depth: float
    data: Union[List[List[int]], List[List[List[int]]]]


@app.get('/imagers/{well_id}')
def get_imager(well_id: str,
               min_depth: float,
               max_depth: float,
               colormap: Optional[str] = None) -> ImagerModel:
    """
    GET: /imagers route handler

    Parameters
    ----------
    well_id : str
        well id
    min_depth : float
        slice from
    max_depth : float
        slice to
    colormap : Optional[str], optional
        name of colormap from `matplotlib.cm` package, by default None

    Returns
    -------
    ImagerModel
        imager data
    """

    img = query_imager(
        well_id=well_id,
        imager_table=os.environ['IMAGERS_TABLE'],
        min_depth=min_depth,
        max_depth=max_depth,
        colormap=colormap,
        region_name=os.environ['REGION']
    )

    if len(img) == 0:
        raise HTTPException(status_code=404, detail="Well or depth range in a well weren't found")

    return ImagerModel(
        well_id=well_id,
        min_depth=min_depth,
        max_depth=max_depth,
        data=img.tolist())

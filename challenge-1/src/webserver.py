
import os
from dataclasses import dataclass
from typing import List, Optional

import boto3
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from challenge1.data import NetGenerationData

app = FastAPI()


class PlanNetGenerationModel(BaseModel):
    plant_name: str
    state: str
    annual_netgen_abs: float
    annual_netgen_rel: float


@dataclass
class Config:
    datamart_bucket: str
    datamart_key_prefix: str
    cache_dir: str

    @staticmethod
    def get() -> 'Config':
        return Config(
            datamart_bucket=os.environ['DATAMART_BUCKET'],
            datamart_key_prefix=os.environ['DATAMART_KEY_PREFIX'],
            cache_dir='./.cache'
        )


def get_datafile(year: int) -> str:
    config = Config.get()

    key = f"{config.datamart_key_prefix}{year}"
    local_path = os.path.join(config.cache_dir, key)

    if not os.path.exists(local_path):
        s3 = boto3.client('s3')
        os.makedirs(config.cache_dir, exist_ok=True)
        s3.download_file(config.datamart_bucket, key, local_path)

    return local_path


def convert(data: NetGenerationData) -> List[PlanNetGenerationModel]:
    result = []
    for _, row in data.df.iterrows():
        item = PlanNetGenerationModel(
            plant_name=row['plant_name'],
            state=row['state'],
            annual_netgen_abs=row['annual_netgen_abs'],
            annual_netgen_rel=row['annual_netgen_rel']
        )
        result.append(item)
    return result


@app.get("/plants")
def get_plants(year: int,
               top_n: Optional[int] = None,
               state: Optional[str] = None) -> List[PlanNetGenerationModel]:

    try:
        path = get_datafile(year)
    except Exception as ex:
        print(ex)  # @TODO replace with proper logging
        raise HTTPException(status_code=404, detail="Data for this year is not found")

    data = pd.read_parquet(path, **NetGenerationData.STORAGE_FORMAT['read_params'])
    data = NetGenerationData(data)

    if state is not None:
        data.df = data.df.loc[data.df.state == state]

    if top_n is not None:
        data.df = data.df[:top_n]

    return convert(data)

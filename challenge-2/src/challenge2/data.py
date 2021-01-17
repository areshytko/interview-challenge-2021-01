

import numpy as np
import pandas as pd
from datautils.typed import TypedDataFrame


class RawImagerData(TypedDataFrame):

    VERSION = '1.0.0'

    schema = {
        'depth': np.float64
    }

    PIXEL_COLUMNS = 200
    PIXEL_DTYPE = np.uint8
    DEPTH_PRECISION_DIGITS = 1

    STORAGE_FORMAT = {
        'file_type': 'csv',
        'read_params': {}
    }

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

        assert len(df.columns) == self.PIXEL_COLUMNS + 1
        for col in df.columns[1:]:
            assert df[col].dtype == self.PIXEL_DTYPE

    @classmethod
    def convert(cls, df: pd.DataFrame) -> 'RawImagerData':
        df = df.copy()
        if df.depth.dtype != cls.schema['depth']:
            df.depth = df.depth.astype(cls.schema['depth']).round(cls.DEPTH_PRECISION_DIGITS)
        for col in df.columns[1:]:
            if df[col].dtype != cls.PIXEL_DTYPE:
                df[col] = df[col].astype(cls.PIXEL_DTYPE)

        return cls(df)

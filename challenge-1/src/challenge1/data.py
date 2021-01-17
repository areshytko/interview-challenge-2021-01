"""
"""

import numpy as np
from datautils.typed import TypedDataFrame


class RawNetGenerationData(TypedDataFrame):

    VERSION = '1.0.0'

    schema = {
        'PNAME': object,  # str
        'PSTATABB': object,  # str
        'PLNGENAN': np.float32
    }

    STORAGE_FORMAT = {
        'file_type': 'excel',
        'read_params': {
            'sheet_name': 'PLNT18',
            'header': 1
        }
    }


class NetGenerationData(TypedDataFrame):
    """
    """

    VERSION = '1.0.0'

    schema = {
        'plant_name': object,  # str
        'state': 'category',  # str
        'annual_netgen_abs': np.float32,
        'annual_netgen_rel': np.float32
    }

    STORAGE_FORMAT = {
        'file_type': 'parquet',
        'read_params': {
            'engine': 'fastparquet'
        },
        'write_params': {
            'engine': 'fastparquet',
            'compression': 'gzip'
        }
    }

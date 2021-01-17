"""
preprocessing functionality
"""

import pandas as pd

from challenge1.data import NetGenerationData, RawNetGenerationData

NAME_CONVERSION = {
    'PNAME': 'plant_name',
    'PSTATABB': 'state',
    'PLNGENAN': 'annual_netgen_abs'
}


def read_raw_data(input_path: str) -> RawNetGenerationData:
    data = pd.read_excel(input_path, **RawNetGenerationData.STORAGE_FORMAT['read_params'])
    return RawNetGenerationData.convert(data)


def preprocess(input_path: str, output_path: str):
    """
    Computes relative annual net generation data, filters invalid data,
    stores the data to the datamart format.

    Parameters
    ----------
    input_path : str
        local FS path to the input data in RawNetGenerationData format
    output_path : str
        local FS path to store the output data in NetGenerationData format
    """
    data = read_raw_data(input_path)
    data = filter_invalid(data).df
    data = data.rename(columns=NAME_CONVERSION)[sorted(NAME_CONVERSION.values())]

    state_aggregate = (data.groupby("state")['annual_netgen_abs']
                       .sum()
                       .reset_index()
                       .rename(columns={"annual_netgen_abs": "state_netgen"}))
    data = pd.merge(data, state_aggregate, on='state')
    data['annual_netgen_rel'] = data.annual_netgen_abs / data.state_netgen

    data = (data.drop('state_netgen', axis=1)
            .sort_values(by='annual_netgen_abs', ascending=False))
    data = NetGenerationData.convert(data)

    data.df.to_parquet(output_path, **NetGenerationData.STORAGE_FORMAT['write_params'])


def filter_invalid(data: RawNetGenerationData) -> RawNetGenerationData:
    """
    Invalid data filtering:
    - NaNs are dropped
    - negative annual net generation data is assumed as invalid and is dropped
    """
    data = data.df.dropna(subset=data.dtype().keys())
    data = data.loc[data.PLNGENAN >= 0]
    return RawNetGenerationData(data)

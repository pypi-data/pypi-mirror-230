from fastapi import APIRouter
from pydantic import BaseModel
from spotfire_dsml.time_series import preprocessing
import pandas as pd
import numpy as np

class MissingValueImputationRequest(BaseModel):
    ts: dict
    index: str, int
    numeric_method: str
    non_numeric_method: str
    numeric_constant: int, float
    non_numeric_constant: str
    warning_threshold: int, float
    n_previous: int

class ResamplingRequest(BaseModel):
    ts: dict
    index: str, int
    rule: str
    n_samples: int
    fill_method: str
    sort: bool

class MinMaxNormalizationRequest(BaseModel):
    ts: dict
    new_min: int, float
    new_max: int, float

class IndexNormalizationRequest(BaseModel):
    ts: dict
    index: str, int
    new_min: int, float
    new_max: int, float
    dt_format: str

router = APIRouter(
    prefix="/time_series",
    tags=["time_series"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def missing_value_imputation(missing_value_imputation_request: MissingValueImputationRequest):
    """Imputing time series for missing values.

    Args:
        missing_value_imputation_request: json structure with the following fields
        ts : data frame
            A data frame where a column is the timestamp or index and all of the
            other columns are readings of variables at corresponding timestamps.
            The number of columns can be an arbitrary number. The values can be
            numeric or non-numeric such as categorical (dictionary) or string. Required.
        index : str, int
            The index/timestamp column: if string it is interpreted as the name
            of the column. Value of -1 indicates that there is no index column and
            the function will create the index column. Required.
        numeric_method : str, int
            Type of imputation for numeric variables. Default = "previous".
            Options:
                0 or “nearest”
                1 or “constant” (constant specified with “numeric_constant”)
                2 or “previous”
                3 or “next”
                4 or “linear”
                5 or “mean”
                6 or “mean_over_n_previous”
                7 or “median_over_n_previous”
        non_numeric_method : str, int
            Type of imputation for non-numeric variables. Default = "previous".
            Options:
                0 or “nearest”
                1 or “constant”
                2 or “previous”
                3 or “next”
        numeric_constant : int, float, numeric
            The numeric constant to be used when the type of numeric imputation
            is set to “constant”. Ignored when “numeric_method” is not
            constant. Default = 0.
        non_numeric_constant : str
            The non-numeric constant to be used when the type of non-numeric
            imputation is set to “constant”. Ignored when “non_numeric_method”
            is not constant. Default = N/A.
        n_previous : int
            The number of past values to include in calculation when
            “mean_over_n_previous” or “median_over_n_previous” is set for the numeric
            imputation, ignored otherwise. Default = 3.
        warning_threshold : float
            A factor that describes the minimum fraction of missing values per column
            needed to invoke a warning to the user. Default = 0.5.

    Raises:
        ValueError: ValueError will be raised if the correlation method
                    specified is wrong or not enough features are selected

    Returns:
        pd.DataFrame: A dataframe with missing values imputed will be returned
    """
    df = pd.json_normalize(missing_value_imputation_request.data)

    result = preprocessing.missing_value_imputation(
        df,
        missing_value_imputation_request.index,
        missing_value_imputation_request.numeric_method or "previous",
        missing_value_imputation_request.non_numeric_method or "previous",
        missing_value_imputation_request.numeric_constant or 0,
        missing_value_imputation_request.non_numeric_constant or "N/A",
        missing_value_imputation_request.n_previous or 3,
        missing_value_imputation_request.warning_threshold or 0.5
    )

    return result

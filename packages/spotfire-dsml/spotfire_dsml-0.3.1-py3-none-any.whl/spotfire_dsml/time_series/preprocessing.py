import pandas as _pd
import numpy as _np
import warnings as _warnings
from datetime import datetime as _datetime
from pandas.api.types import is_numeric_dtype as _is_numeric_dtype

_formatwarning_orig = _warnings.formatwarning
_warnings.formatwarning = lambda message, category, filename, lineno, line=None: _formatwarning_orig(message, category, filename, lineno, line='')

def _numeric_imputation(col, method, optional_args):
    warn = optional_args.get("warning_threshold")
    if col.isna().sum() >= (len(col) * warn):
        _warnings.warn('Warning: column "{}" contains more than {}% NaNs. Please consider further evaluation prior to imputation.'.format(col.name, int(warn * 100)))
    if method in ("nearest", 0):
        return col.interpolate("nearest").ffill().bfill()
    elif method in ("constant", 1):
        return col.fillna(optional_args.get("numeric_constant"))
    elif method in ("previous", 2):
        return col.fillna(method="ffill")
    elif method in ("next", 3):
        return col.fillna(method="bfill")
    elif method in ("linear", 4):
        return col.interpolate(method="linear")
    elif method in ("mean", 5):
        return col.fillna(col.mean())
    elif method in ("mean_over_n_previous", 6):
        return col.fillna(col.rolling(optional_args.get("n_previous"), min_periods=1).mean().shift(1))
    elif method in ("median_over_n_previous", 7):
        return col.fillna(col.rolling(optional_args.get("n_previous"), min_periods=1).median().shift(1))
    else:
        raise Exception("numeric_method not recognized, please try again.")

def _non_numeric_nearest(col):
    factors = col.factorize()
    factors_with_nan = _pd.Series(factors[0], col.index).replace(-1, _np.nan)
    factors_interpolated = factors_with_nan.interpolate("nearest").ffill().bfill()
    return factors_interpolated.map(dict(enumerate(factors[1])))
    
def _non_numeric_imputation(col, method, optional_args):
    warn = optional_args.get("warning_threshold")
    if col.isna().sum() >= (len(col) * warn):
        _warnings.warn('Warning: column "{}" contains more than {}% NaNs. Please consider further evaluation prior to imputation.'.format(col.name, int(warn * 100)))
    if method in ("nearest", 0):
        return _non_numeric_nearest(col)
    elif method in ("constant", 1):
        return col.fillna(optional_args.get("non_numeric_constant"))
    elif method in ("previous", 2):
        return col.fillna(method="ffill")
    elif method in ("next", 3):
        return col.fillna(method="bfill")
    else:
        raise Exception("non_numeric_method not recognized, please try again.")
    
def missing_value_imputation(ts, index, numeric_method="previous", non_numeric_method="previous", 
                             numeric_constant=0, non_numeric_constant="N/A", warning_threshold=0.5,
                             n_previous=3):
    """
    Imputing time series for missing values.

    Parameters
    ----------
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

    Returns
    -------
    ts
        ts with missing values imputed, same dimensions.

    Examples
    --------
    >>> ex = pd.DataFrame({"Date": pd.date_range("2015-01-01", "2015-01-05"), 
                           "Temp": [80, np.nan, 95, 76, np.nan],
                           "Events": ["Fog", np.nan, np.nan, "Fog", np.nan]})
    >>> missing_value_imputation(ex, "Date")
        Date		Temp	Events
    0	2015-01-01	80.00	Fog
    1	2015-01-02	83.67	Fog
    2	2015-01-03	95.00	Fog
    3	2015-01-04	76.00	Fog
    4	2015-01-05	83.67	Fog
    >>> missing_value_imputation(ex, "Date", numeric_method="mean_over_n_previous",
                                 non_numeric_method="constant", n_previous=2)
        Date		Temp	Events
    0	2015-01-01	80.0	Fog
    1	2015-01-02	80.0	N/A
    2	2015-01-03	95.0	N/A
    3	2015-01-04	76.0	Fog
    4	2015-01-05	85.5	N/A
    >>> missing_value_imputation(ex, "Date", numeric_method="linear",
                                 non_numeric_method="nearest")
        Date		Temp	Events
    0	2015-01-01	80.0	Fog
    1	2015-01-02	87.5	Fog
    2	2015-01-03	95.0	Fog
    3	2015-01-04	76.0	Fog
    4	2015-01-05	76.0	Fog
    """
    ts = ts.copy()
    args = locals()
    if index is None or index == -1: #add index if none exists
        index = "index"
        ts[index] = _np.arange(len(ts))
    numeric_cols = ts.select_dtypes("number").columns #separate numeric
    non_numeric_cols = ts.select_dtypes(exclude="number").columns #separate non-numeric
    # apply imputation to numeric and non-numeric columns
    ts[numeric_cols] = ts[numeric_cols].apply(lambda x: _numeric_imputation(x, method=numeric_method, optional_args=args))
    ts[non_numeric_cols] = ts[non_numeric_cols].apply(lambda x: _non_numeric_imputation(x, method=non_numeric_method, optional_args=args))
    return ts

def resampling(ts, index, rule=None, n_samples=None, fill_method="previous", sort=False):
    """
    Resampling time series data.
    
    This function returns a copy of the input time series resampled with
    a new desired frequency, specified by either a datetime rule or number
    of samples. Indices/timestamps will regular and equally distanced from 
    each other.

    Parameters
    ----------
    ts : data frame
        A data frame where a column is the timestamp or index and all of the
        other columns are readings of variables at corresponding timestamps.
        The number of columns can be an arbitrary number. The values can be 
        numeric or non-numeric such as categorical (dictionary) or string. Required.
    index : str
        The index/timestamp column. Required.
    rule : str
        Rule that represents how and at what frequency the timestamps will be 
        resampled. Examples: ("12H": 12 hours), ("3D": 3 days), ("Y", year)
        Full list of frequency strings can be found at:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
    n_samples : int
        Number of samples desired at completion of resampling process. If this
        input is present, “rule” will be ignored.
    fill_method : str, int
        Determines what method to either fill missing values introduced by 
        upsampling or aggregate values from downsampling. Default = "previous".
        Options:
            0 or “nearest”
            1 or “linear”
            2 or “previous”
            3 or “next”
            “mean” (only available when n_samples < len(ts))
            “median” (only available when n_samples < len(ts))
            “sum” (only available when n_samples < len(ts))
    sort : boolean
        If True, the function will sort the rows by the index. Default = False.

    Returns
    -------
    ts
        resampled copy of ts with desired frequency.

    Examples
    --------
    >>> ex = pd.DataFrame({"Date": pd.date_range("2015-01-01", "2015-01-05"), 
                           "Temp": [80, np.nan, 95, 76, np.nan],
                           "Events": ["Fog", np.nan, np.nan, "Fog", np.nan]})
    >>> resampling(ex, "Date", rule="12H")
        Date			Temp	Events
    0	2015-01-01 00:00:00	80.0	Fog
    1	2015-01-01 12:00:00	80.0	Fog
    2	2015-01-02 00:00:00	NaN	NaN
    3	2015-01-02 12:00:00	NaN	NaN
    4	2015-01-03 00:00:00	95.0	NaN
    5	2015-01-03 12:00:00	95.0	NaN
    6	2015-01-04 00:00:00	76.0	Fog
    7	2015-01-04 12:00:00	76.0	Fog
    8	2015-01-05 00:00:00	NaN	NaN
    >>> resampling(ex, "Date", n_samples=4, fill_method="nearest")
        Date			Temp	Events
    0	2015-01-01 00:00:00	80.0	Fog
    1	2015-01-02 08:00:00	NaN	NaN
    2	2015-01-03 16:00:00	76.0	Fog
    3	2015-01-05 00:00:00	NaN	NaN
    >>> resampling(ex, "Date", n_samples=3, fill_method="mean")
        Date		Temp	Events
    0	2015-01-01	80.0	Fog
    1	2015-01-03	85.5	NaN
    2	2015-01-05	NaN	NaN
    """
    ts = ts.copy()
    agg_methods = ["sum", "mean", "median"]
    numeric_cols = ts.select_dtypes("number").columns
    non_numeric_cols = ts.select_dtypes(exclude="number").columns
    if sort:
        ts = ts.sort_values(index)
    if not _is_numeric_dtype(ts[index]):
        ts[index] = _pd.to_datetime(ts[index])
        ts.index = ts[index]
    if n_samples:
        if (n_samples > len(ts)) and (fill_method in agg_methods):
            raise Exception("Aggregation methods are not allowed for upsampling. Please use a different fill_method.")
        idx_min = min(ts.index)
        idx_max = max(ts.index)
        try:
            resampled_index = _pd.Series(_np.linspace(idx_min, idx_max, num=n_samples))
        except:
            resampled_index = _pd.to_datetime(_np.linspace(idx_min.value, idx_max.value, num=n_samples))
        resampled_index.name = index
        ts = ts.fillna(_np.inf)
        ts = ts.reindex(ts.index.union(resampled_index))
        if fill_method in ("previous", 2):
            ts = ts.fillna(method="pad")
        elif fill_method in ("next", 3):
            ts = ts.fillna(method="backfill")
        elif fill_method in agg_methods:
            ts = _resample_agg(ts, index, fill_method, resampled_index, numeric_cols, non_numeric_cols)
        else:
            if fill_method in ("nearest", 0):
                ts[numeric_cols] = ts[numeric_cols].infer_objects().apply(lambda x: x.interpolate("nearest"))
                ts[non_numeric_cols] = ts[non_numeric_cols].apply(lambda x: _non_numeric_nearest(x))
            elif fill_method in ("linear", 1):
                ts[numeric_cols] = ts[numeric_cols].infer_objects().apply(lambda x: x.interpolate("linear"))
                ts[non_numeric_cols] = ts[non_numeric_cols].apply(lambda x: _non_numeric_nearest(x))
            else:
                raise Exception("fill_method not recognized, please try again.")
    elif rule:
        if fill_method in agg_methods:
            ts_non_num = ts[non_numeric_cols].resample(rule).fillna("nearest")
            if fill_method == "sum":
                ts_num = ts[numeric_cols].resample(rule).sum()
            elif fill_method == "mean":
                ts_num = ts[numeric_cols].resample(rule).mean()
            elif fill_method == "median": 
                ts_num = ts[numeric_cols].resample(rule).median()
            else:
                raise Exception("fill_method not recognized, please try again.")
            ts = _pd.concat([ts_num, ts_non_num], axis=1)
        else:
            ts = ts.resample(rule)
            if fill_method == "previous":
                ts = ts.fillna(method="pad")
            elif fill_method == "next":
                ts = ts.fillna(method="backfill")
            elif fill_method == "nearest":
                ts = ts.fillna(method="nearest")
            elif fill_method == "linear":
                ts = ts.mean().interpolate("linear")
            else:
                raise Exception("fill_method not recognized, please try again.")
    else:
        raise Exception("No resampling method recognized, please try again.")
    ts = ts.replace(_np.inf, _np.nan)
    try:
        ts = ts.reindex(resampled_index)
    except:
        pass
    return ts.drop(index, axis=1, errors="ignore").reset_index()

def _resample_agg(ts, index, fill_method, resampled_index, numeric_cols, non_numeric_cols):
    ts.index.name = "resampled_index"
    ts = ts.reset_index()
    ts["group"] = ts["resampled_index"].apply(lambda x: _np.searchsorted(resampled_index, x, side="right"))
    group_summary_num = ts.replace(_np.inf, _np.nan).groupby("group")[numeric_cols].agg(fill_method).reset_index()
    if len(non_numeric_cols) > 0:
        group_summary_non_num = ts.groupby("group")[non_numeric_cols].agg(lambda x: _pd.Series.mode(x)[0])
    ts = ts[["resampled_index", "group"]].merge(group_summary_num, on="group")
    if len(non_numeric_cols) > 0:
        ts = ts.merge(group_summary_non_num, on="group")
    return ts.set_index("resampled_index").drop("group", axis=1)

def min_max_normalization(ts, new_min=0, new_max=1):
    """
    Min/Max Normalization of time series data.

    Parameters
    ----------
    ts : data frame
        A data frame where a column is the timestamp or index and all of the
        other columns are readings of variables at corresponding timestamps.
        The number of columns can be an arbitrary number. The values can be 
        numeric or non-numeric such as categorical (dictionary) or string. Required.
    new_min : int, float, numeric
        The new desired minimum. Default = 0.
    new_max : int, float, numeric
        The new desired maximum. Default = 1.

    Returns
    -------
    ts
        Copy of ts with the numeric variables mapped to the new range (Non-numeric
        columns will be remain unchanged).

    Examples
    --------
    >>> ex = pd.DataFrame({"Date": pd.date_range("2015-01-01", "2015-01-05"), 
                           "Temp": [80, np.nan, 95, 76, np.nan],
                           "Events": ["Fog", np.nan, np.nan, "Fog", np.nan]})
    >>> min_max_normalization(ex)
        Date		Temp		Events
    0	2015-01-01	0.210526	Fog
    1	2015-01-02	NaN		NaN
    2	2015-01-03	1.000000	NaN
    3	2015-01-04	0.000000	Fog
    4	2015-01-05	NaN		NaN
    >>> min_max_normalization(ex, -5, 5)
        Date		Temp		Events
    0	2015-01-01	-2.894737	Fog
    1	2015-01-02	NaN		NaN
    2	2015-01-03	5.000000	NaN
    3	2015-01-04	-5.000000	Fog
    4	2015-01-05	NaN		NaN
    """
    if new_min >= new_max:
        raise Exception("new_max must be greater than new_min. Please adjust and try again.")
    ts = ts.copy()
    non_constant_cols = ts.loc[:, (ts != ts.iloc[0]).any()].columns
    numeric_cols = ts.select_dtypes("number").columns
    include_cols = numeric_cols.intersection(non_constant_cols)
    ts[include_cols] = ts[include_cols].apply(lambda x: (((x - _np.nanmin(x)) / (_np.nanmax(x) - _np.nanmin(x))) * \
                                                          (new_max - new_min)) + new_min)
    return ts

def index_normalization(ts, index, new_min, new_max, dt_format):
    """
    Index Normalization of time series data.

    This function stretches, squeezes, or shifts the time index
    of a time series to fit into a desired range.
    
    ----------
    ts : data frame
        A data frame where a column is the timestamp and all of the
        other columns are readings of variables at corresponding timestamps.
        The number of columns can be an arbitrary number. The values can be 
        numeric or non-numeric such as categorical (dictionary) or string. Required.
    index : str
        The timestamp column. Required.
    new_min : str
        The new desired minimum timestamp.
    new_max : str
        The new desired maximum timestamp.
    dt_format : str
        The datetime format of new_min/new_max.
        Examples: ("%m/%d/%y": "3/1/98"), ("%Y-%m-%d": "1998-03-01"), ("%m/%d/%Y %H:%M:%S": "3/1/1998 4:00:00")
        Reference for format codes:
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    Returns
    -------
    ts
        Copy of ts with the index mapped to its new range.

    Examples
    --------
    >>> ex = pd.DataFrame({"Date": pd.date_range("2015-01-01", "2015-01-05"), 
                           "Temp": [80, np.nan, 95, 76, np.nan],
                           "Events": ["Fog", np.nan, np.nan, "Fog", np.nan]})
    >>> index_normalization(ex, "Date", "2015-01-01", "2016-01-01", dt_format="%Y-%m-%d")
        Date			Temp	Events
    0	2015-01-01 00:00:00	80.0	Fog
    1	2015-04-02 06:00:00	NaN	NaN
    2	2015-07-02 12:00:00	95.0	NaN
    3	2015-10-01 18:00:00	76.0	Fog
    4	2016-01-01 00:00:00	NaN	NaN
    >>> index_normalization(ex, "Date", "12-31-14", "1-2-15", dt_format="%m-%d-%y")
        Date			Temp	Events
    0	2014-12-31 00:00:00	80.0	Fog
    1	2014-12-31 12:00:00	NaN	NaN
    2	2015-01-01 00:00:00	95.0	NaN
    3	2015-01-01 12:00:00	76.0	Fog
    4	2015-01-02 00:00:00	NaN	NaN
    """
    ts = ts.copy()
    new_min = _datetime.strptime(new_min, dt_format)
    new_max = _datetime.strptime(new_max, dt_format)
    x = _pd.to_datetime(ts[index])
    ts[index] = (((x - _np.min(x)) / (_np.max(x) - _np.min(x))) * (new_max - new_min)) + new_min
    return ts
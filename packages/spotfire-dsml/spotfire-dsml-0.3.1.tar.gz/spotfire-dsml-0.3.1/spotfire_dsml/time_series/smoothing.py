import pandas as pd
import numpy as np
import warnings as _warnings
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from supersmoother import SuperSmoother
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.stats import norm, logistic
from scipy.special import expit as sigmoid
from datetime import datetime, date, time

def _index_col_helper(index_col, measurement_col):
    if index_col is None:
        x = np.arange(len(measurement_col))
    else:
        x = np.array(index_col)
        if np.any(pd.isnull(x)):
            raise ValueError("index_col contains null values. Please remove or replace them before smoothing.")

    if np.issubdtype(x.dtype, np.datetime64):
        x_numeric = x.astype(int) / 10**9
    elif isinstance(x[0], (datetime, date)):
        x_numeric = np.array([pd.Timestamp(t).timestamp() for t in x])
    elif isinstance(x[0], time):
        x_numeric = np.array([t.hour * 3600 + t.minute * 60 + t.second for t in x])
    elif np.issubdtype(x.dtype, np.number):
        x_numeric = x
    else:
        raise ValueError(f"Unsupported data type for index_col: {x.dtype}")
    return x, x_numeric

def moving_average(measurement_col, moving_average_type="simple", window_size=0.25):
    """
    Calculates the moving average of a measurement column.

    Parameters
    ----------
    measurement_col: array-like
        The measurement column for which to calculate the moving average.
        
    moving_average_type : str, optional (default="simple")
        The type of moving average to compute. Can be "simple", "cumulative", or "exponential"
        
    window_size : float or int, optional (default=0.25)
        The size of the moving window. If a float and < 1, it is interpreted as a proportion of the length of 
        measurement_col. If an integer and > 1, it represents a fixed window size.

    Returns
    -------
    pandas.Series : A column containing the moving average of measurement_col
    
    Examples
    --------
    >>> measurement_col = pd.Series([1,2,3,4,5])
    >>> moving_average(measurement_col, window_size=0.5)
    0    NaN
    1    1.5
    2    2.5
    3    3.5
    4    4.5
    >>> moving_average(measurement_col, moving_average_type="cumulative")
    0    1.0
    1    1.5
    2    2.0
    3    2.5
    4    3.0
    >>> moving_average(measurement_col, moving_average_type="exponential", window_size=0.5)
    0         NaN
    1    1.333333
    2    2.111111
    3    3.000000
    4    3.888889
    
    Notes
    -----
    • The moving average is a common statistical method used to analyze data by smoothing out short-term fluctuations
      and highlighting long-term trends.
    • The "simple" moving average is calculated by taking the average of a set of consecutive data points.
    • The "cumulative" moving average is calculated by taking the cumulative sum of the data and dividing by 
      the number of data points at each point.
    • The "exponential" moving average is calculated using a weighting factor such that more recent data points are given
      higher weight.
    • The window_size parameter determines how many data points are included in the moving average calculation.
      A larger window size will result in a smoother moving average, but may also introduce more lag.
    """
    if window_size < 1: window_size = int(window_size * len(measurement_col))
    if moving_average_type == "cumulative":
        return measurement_col.expanding().mean()
    elif moving_average_type == "exponential":
        return measurement_col.ewm(span=int(window_size)).mean()
    else:
        if moving_average_type != "simple":
            _warnings.warn("moving_average_type not recognized, default 'simple' used.")
        return measurement_col.rolling(int(window_size)).mean()

def simple_exponential(measurement_col, smoothing_level=0.25):
    """
    Calculates the simple exponential smoothing of a measurement column.

    Parameters
    ----------
    measurement_col : array-like
        The measurement column for which to calculate the simple exponential smoothing.
        
    smoothing_level : float, optional (default=0.25)
        The smoothing level for the simple exponential smoothing. A high value gives more weight
        to the most recent observation and therefore produces a smoother curve. A low value gives less
        weight to the most recent observation and therefore produces a curve with more fluctuations.
        The value should be a float between 0 and 1.
    
    Returns
    -------
        pandas.Series : A column containing the simple exponential smoothing of measurement_col
    
    Examples
    --------
    >>> measurement_col = pd.Series([1,2,3,4,5])
    >>> simple_exponential(measurement_col, smoothing_level=0.1)
    0    1.000000
    1    1.090909
    2    1.272727
    3    1.553097
    4    1.939907
    >>> simple_exponential(measurement_col, smoothing_level=0.5)
    0    1.000000
    1    1.333333
    2    2.111111
    3    3.000000
    4    3.888889
    >>> simple_exponential(measurement_col, smoothing_level=0.9)
    0    1.000000
    1    1.900000
    2    3.610000
    3    6.539100
    4    12.100481
    
    Notes
    -----
    • Simple exponential smoothing is a technique used for smoothing time series data that does not have a
      clear trend or seasonality. It is particularly useful for data that has a lot of noise or random fluctuations.
      The technique works by taking a weighted average of past observations, with the weight for each observation
      decreasing exponentially as the observation gets older. This allows the more recent observations to have a 
      greater influence on the smoothed data.
    """
    if smoothing_level < 0 or smoothing_level > 1:
        _warnings.warn("smoothing_level outside of recommended range of 0-1, use caution when evaluating results.")
    model = SimpleExpSmoothing(measurement_col)
    return model.fit(smoothing_level=smoothing_level, optimized=False).fittedvalues

def supersmoothing(measurement_col, alpha=None, index_col=None):
    """
    Calculates Friedman"s Supersmoother on a measurement column.

    Parameters
    ----------
    measurement_col: array-like
        The measurement column for which to calculate the super smoothing.
        
    alpha: float, optional (default=None)
        The value of alpha must be between 0 and 1. A value of 0 corresponds to no smoothing (i.e., the raw
        data is returned), and a value of 1 corresponds to maximum smoothing (i.e., a straight line is fit
        to the data). In general, a value of alpha between 0.2 and 0.5 is recommended for most data sets.
        If None, the optimal smoothing parameter will be determined using the Akaike information criterion.
        
    index_col : array-like, optional (default=None)
        The index of the input data. If None, an evenly spaced integer index is created.
        Supports datetime.date, datetime.datetime, datetime.time, integer, and float data types.
        
    Returns
    -------
        pandas Series: A column containing the supersmoothing of measurement_col
        
    Examples
    --------
    >>> measurement_col = pd.Series([1,2,3,4,5])
    >>> supersmoothing(measurement_col)
    0    1.000000
    1    1.166667
    2    2.000000
    3    2.857143
    4    3.600000
    
    Notes
    -----
    • Friedman's Supersmoother is a non-parametric smoothing technique that is designed to produce a smooth curve
      that effectively captures both the underlying trend and the fluctuations in the data. The technique was
      proposed by Jerome Friedman in 1994 and it is an extension of the popular loess smoothing technique.
    • When alpha is set to None, the optimal smoothing parameter will be determined using the Akaike 
      information criterion (AIC). The AIC is a measure of the relative quality of a statistical model for 
      a given set of data. The AIC criterion is used to select the value of alpha that gives the best balance
      between goodness of fit and complexity of the model.
    """
    x, x_numeric = _index_col_helper(index_col, measurement_col)
    if len(measurement_col) < 100:
        try:
            return pd.Series(SuperSmoother(primary_spans=(0.25, 0.35, 0.5),
                                           middle_span=0.35,
                                           final_span=0.25,
                                           alpha=alpha).fit(x_numeric, measurement_col).ysmooth_raw,
                             index=x)
        except Exception as e:
            raise Exception("An error occurred during smoothing: {} Please make sure there are enough distinct data points to compute the smoother.".format(e))
    return pd.Series(SuperSmoother(alpha=alpha).fit(x_numeric, measurement_col).ysmooth_raw, index=x)

def loess(measurement_col, span=0.25, index_col=None):
    """
    Performs LOESS (locally estimated scatterplot smoothing) on a measurement column.

    Parameters
    ----------
    measurement_col : array-like
        The measurement column for which to calculate LOESS smoothing.
        
    span : float, optional (default=0.25)
        Either the proportion of data points to use for each local fit (0-1), or
        the explicit number of data points to use (>1).
        
    index_col : array-like, optional (default=None)
        The index of the input data. If None, an evenly spaced integer index is created.
        Supports datetime.date, datetime.datetime, datetime.time, integer, and float data types.
    
    Returns
    -------
        pandas Series : A column containing the LOESS smoothed version of measurement_col.
        
    Examples
    --------
    >>> measurement_col = pd.Series([1,2,3,4,4,3,2,1])
    >>> loess(measurement_col, 0.75)
        0    1.000000
        1    2.000000
        2    3.000000
        3    2.887559
        4    2.835148
        5    3.000000
        6    2.000000
        7    1.000000
    >>> loess(measurement_col, 1)
        0    1.455558
        1    2.062690
        2    2.596681
        3    3.076970
        4    3.076970
        5    2.596681
        6    2.062690
        7    1.455558
    >>> loess(measurement_col, 5)
        0    1.0
        1    2.0
        2    3.0
        3    3.5
        4    4.0
        5    3.0
        6    2.0
        7    1.0
        
    Notes
    -----
    • LOESS may be preferred in cases where the time series has non-linear patterns or is sensitive to
      outliers, as it can effectively capture these patterns and reduce the impact of outliers on the smoothed
      line.
    • A smaller span will result in a smoother line but may not capture the local variability of the data
      as well. A larger span will capture more local variability but may also introduce more noise into the
      smooth line.
    """
    if span > 1:
        span = span / len(measurement_col)
    x, x_numeric = _index_col_helper(index_col, measurement_col)
    return pd.Series(lowess(endog=measurement_col, exog=x_numeric, frac=span, return_sorted=False, missing="none"), index=x)

def fourier(measurement_col, pct_to_keep=0.5):
    """
    Applies a Fourier transform-based smoothing to a measurement column.

    Parameters
    ----------
    measurement_col : array-like
        The measurement column for which to calculate LOESS smoothing.
        
    pct_to_keep : float, optional (default = 0.5)
        A value between 0 and 1 that determines the percentage of high-frequency components
        to be retained after the smoothing process.
    
    Returns
    -------
        pandas Series : A column containing the Fourier smoothed version of measurement_col.
        
    
    Examples
    --------
    >>> measurement_col = pd.Series([1, 2, 3, 4, 3, 4, 3, 2, 1])
    >>> fourier(measurement_col)
        0    1.060737
        1    1.825114
        2    3.267942
        3    3.671321
        4    3.349773
        5    3.671321
        6    3.267942
        7    1.825114
        8    1.060737
    >>> fourier(measurement_col, 0.25)
        0    1.241895
        1    1.856571
        2    2.798310
        3    3.626462
        4    3.953524
        5    3.626462
        6    2.798310
        7    1.856571
        8    1.241895
        
    Notes
    -----
    • This function takes a measurement column and applies a real-valued fast Fourier transform (rfft)
      to it, which decomposes the signal into its frequency components. Then, it sets to zero all but a
      certain percentage (determined by the filter_pct parameter) of the highest frequency components,
      effectively filtering out high-frequency noise. Finally, it applies the inverse Fourier transform 
      (irfft) to the filtered signal to obtain a smoothed version of the original measurement column.
    • The main advantage of using a Fourier transform-based smoother is that it allows for the separation
      of a signal's high-frequency and low-frequency components, which can be useful in cases where the
      noise is mostly concentrated in the high-frequency range. This can be particularly beneficial in signals
      with sharp transitions or discontinuities, where other smoothing methods such as moving averages might
      not work as well.
    • The pct_to_keep parameter determines the percentage of high-frequency components that will be kept
      in the signal after the smoothing process. A value of 0.5, for example, will keep the 50% of the highest
      frequency components, while a value of 0.1 will keep only the 10% of the highest frequency components.
    """
    if pct_to_keep > 1:
        pct_to_keep = pct_to_keep / 100
    if pct_to_keep < 0 or pct_to_keep > 1:
        _warnings.warn("pct_to_keep outside of range 0-1, using default of '0.5'")
        pct_to_keep = 0.5
    rft = np.fft.rfft(measurement_col)
    rft[int(pct_to_keep * len(measurement_col)):] = 0
    return pd.Series(np.fft.irfft(rft, n=len(measurement_col)))

def kernel_weighted_average(measurement_col=None, smoothing_level=0.1, kernel="gaussian", index_col=None):
    """
    Smooths the input data using a kernel-weighted average method.
    
    Parameters
    ----------
    measurement_col : array-like
        The measurement values to be smoothed.
     
    smoothing_level : float, optional (default=0.5)
        The level of smoothing to apply. A value between 0 and 1, where 0 is least smoothed
        and 1 is the most smoothed.
        
    kernel : str, optional (default="gaussian")
        The kernel function to use for smoothing. Supported options are:
        • "gaussian": Gaussian kernel, smooth and differentiable but has infinite support.
        • "logistic": Logistic kernel, similar to Gaussian but has a heavier tail.
        • "sigmoid": Sigmoid kernel, can produce sharp transitions in the smoothed data.
        • "epanechnikov": Epanechnikov kernel, has compact support and is smoother than Gaussian.
                          Computationally efficient and often used in practice.
        • "triangular": Triangular kernel, a simple linear function that decreases as you move
                        away from the center. Easy to compute and can produce smooth curves.
        • "quartic": Quartic (biweight) kernel, smoother than Epanechnikov and often used
                     in practice due to its smoothness properties.
                     
    index_col : array-like, optional (default=None)
        The index of the input data. If None, an evenly spaced integer index is created.
        Supports datetime.date, datetime.datetime, datetime.time, integer, and float data types.
        
    Returns
    -------
        pandas Series : smoothed measurement values
        
    Examples
    --------
    >>> measurement_col = pd.Series([1, 2, 3, 4, 3, 4, 3, 2, 1])
    >>> kernel_weighted_average(measurement_col)
        0    1.364931
        1    2.045277
        2    2.956601
        3    3.497792
        4    3.455731
        5    3.497792
        6    2.956601
        7    2.045277
        8    1.364931
    >>> kernel_weighted_average(measurement_col, smoothing_level=0.5, kernel="epanechnikov")
        0    2.200000
        1    2.476923
        2    2.779221
        3    3.023810
        4    3.190476
        5    3.023810
        6    2.779221
        7    2.476923
        8    2.200000
    >>> kernel_weighted_average(measurement_col, smoothing_level=0.25, kernel="triangular")
        0    1.333333
        1    2.000000
        2    3.000000
        3    3.500000
        4    3.500000
        5    3.500000
        6    3.000000
        7    2.000000
        8    1.333333
    
    Notes
    -----
    • The choice of kernel and smoothing_level depends on the specific problem and the nature
      of the data. It is often a good idea to try different kernels and smoothing levels to
      see which one provides the best results for your application.
    • The smoothing_level parameter controls the amount of smoothing by adjusting the bandwidth
      of the kernel. A smaller bandwidth (closer to 0) results in less smoothing and a larger
      bandwidth (closer to 1) results in more smoothing. You can adjust the smoothing_level
      based on the level of noise present in the data and the desired degree of smoothing.
    • In general, the Gaussian and Epanechnikov kernels are good choices for most applications
      due to their smoothness properties and computational efficiency. However, other kernels
      may be more suitable for specific problems or when certain characteristics are desired
      in the smoothed data.
    """
    def gaussian_kernel(x):
        return norm.pdf(x, scale=bandwidth)

    def logistic_kernel(x):
        return logistic.pdf(x, scale=bandwidth)

    def sigmoid_kernel(x):
        return sigmoid(-x / bandwidth)

    def epanechnikov_kernel(x):
        return np.where(np.abs(x) <= bandwidth, 3 / (4 * bandwidth) * (1 - (x / bandwidth) ** 2), 0)

    def triangular_kernel(x):
        return np.where(np.abs(x) <= bandwidth, (1 - np.abs(x) / bandwidth) / bandwidth, 0)

    def quartic_kernel(x):
        return np.where(np.abs(x) <= bandwidth, 15 / (16 * bandwidth) * (1 - (x / bandwidth) ** 2) ** 2, 0)

    kernel_dict = {
        "gaussian": gaussian_kernel,
        "logistic": logistic_kernel,
        "sigmoid": sigmoid_kernel,
        "epanechnikov": epanechnikov_kernel,
        "triangular": triangular_kernel,
        "quartic": quartic_kernel
    }

    kernel_func = kernel_dict.get(kernel.lower())
    if kernel_func is None:
        raise ValueError(f"Invalid kernel type. Supported kernels: {list(kernel_dict.keys())}")

    x, x_numeric = _index_col_helper(index_col, measurement_col)
    y = np.array(measurement_col)
    if np.any(pd.isnull(y)):
        raise ValueError("measurement_col contains null values. Please remove or replace them before smoothing.")

    smoothing_level = np.clip(smoothing_level, 0, 1)
    smoothing_level = smoothing_level**2 #to scale smoothing_level
    bandwidth = (x_numeric.max() - x_numeric.min()) * smoothing_level

    smoothed_y = np.zeros(len(y))
    for i in range(len(y)):
        x_diff = np.float64(x_numeric[i] - x_numeric)
        weights = kernel_func(x_diff)
        smoothed_y[i] = np.average(y, weights=weights)

    return pd.Series(smoothed_y, index=x)
import warnings

import numpy as np
import pandas as pd

# import the contents of the Rust library into the Python extension
# optional: include the documentation from the Rust module
# __all__ = __all__ + ["PythonClass"]


def add_one(x: int) -> int:
    """see if documentation works

    Args:
        x (int): your number

    Returns:
        int: numnber +1
    """
    return x + 1



def __validate__prices__(prices):

    if isinstance(prices, pd.DataFrame):
        assert(set(prices.index).issubset({'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'}))
        prices_df = prices

    if isinstance(prices, dict):
        if all([isinstance(p, dict) for p in prices.values()]):
            prices_df = pd.DataFrame(prices)
        if all([(isinstance(p, pd.Series) or isinstance(p, np.ndarray)) for p in prices.values()]):
            prices_df = pd.DataFrame(prices).T
        assert(set(prices_df.index).issubset({'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'}))

    if callable(prices):
        raise NotImplemented("Not Implemented Yet")

    try:
        return prices_df
    except UnboundLocalError:
        raise TypeError("prices must be either pd.DataFrame, dict or Callable")

def __find_period__(df: pd.DataFrame) -> str:
        if isinstance(df.index, pd.PeriodIndex):
            return df.index.freqstr
        else:
            dates = pd.to_datetime(df.index)
        periods = np.diff(dates, 1)
        if periods.min() != periods.max():
            warnings.warn("Careful, you have missing datas in your usage")
        return dates.inferred_freq


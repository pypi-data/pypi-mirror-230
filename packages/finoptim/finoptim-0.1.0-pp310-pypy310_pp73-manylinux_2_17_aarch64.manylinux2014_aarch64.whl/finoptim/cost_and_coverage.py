import numpy as np
import pandas as pd

# import the contents of the Rust library into the Python extension
# optional: include the documentation from the Rust module
# __all__ = __all__ + ["PythonClass"]

import finoptim.rust_as_backend as rs
from finoptim.validations import __validate__prices__, __find_period__


from typing import Optional, List, Union


def cost(usage: Union[pd.DataFrame, np.ndarray],
         prices: Union[dict, list, np.ndarray],
         commitments: Optional[dict]=None,
         savings_plans: Union[None, float, int, np.ndarray]=None,
         reservations: Union[None, np.ndarray, dict]=None,
         period: Optional[str]=None,
         guid: Optional[List[str]]=None) -> float:
    """compute cost based on usage.

    Args:
        usage (Union[pd.DataFrame, np.ndarray]): Cloud usage in hours or days. The DataFrame index must be the time.
        prices (Union[dict, list, np.ndarray]): Prices associated with different pricing models
        commitments (Optional[dict], optional): 
            A dictionnary of the different commitments. The keys must be RI or SP for reserved instances 
            and savings plans, followed by the term. in years. For exemple : 'RI3Y' or 'SP1Y'.
            If commitments is specified, `savings_plans` and `reservations` can be left to `None`
        savings_plans (Union[None, float, int, np.ndarray], optional): Savings plans commitment per hour or day
        reservations (Union[None, np.ndarray, dict], optional): Reservations levels per families. One per usage columns, or dict with keys same as usage columns
        period (Optional[str], optional): Time period of usage. Defaults to None.
        guid (Optional[List[str]], optional): to implement, column with guids in case of long DataFrame. Defaults to None.

    Raises:
        Exception: Negative reservation not allowed
        Exception: Can't infer the series period

    Returns:
        float: the cost associated with the usage, prices and input levels of commitments

        the savings plans levels must be the ammount of money spend per time period (hours or days)
    """

    return __general_entries__("cost", usage, prices, commitments, savings_plans, reservations, period, guid)



def coverage(usage: Union[pd.DataFrame, np.ndarray],
         prices: Union[dict, list, np.ndarray],
         commitments: Optional[dict]=None,
         savings_plans: Union[None, float, int, np.ndarray]=None,
         reservations: Union[None, np.ndarray, dict]=None,
         period: Optional[str]=None,
         guid: Optional[List[str]]=None) -> float:
    """compute coverage based on usage.


    
    How coverage is defined ?

    Coverage is defined as the on demand equivalent cost of the usage running
    reserved or with savings plans, divided by the total on demand equivalent usage.

    .. math::
        y = \frac{x - \mathrm{E}[x]}{ \sqrt{\mathrm{Var}[x] + \epsilon}} * \gamma + \beta
        is maths formulas used by the linter ?
    
    Args:
        usage (Union[pd.DataFrame, np.ndarray]): Cloud usage in hours or days. The DataFrame index must be the time.
        prices (Union[dict, list, np.ndarray]): Prices associated with different pricing models
        commitments (Optional[dict], optional): 
            A dictionnary of the different commitments. The keys must be RI or SP for reserved instances 
            and savings plans, followed by the term. in years. For exemple : 'RI3Y' or 'SP1Y'.
            If commitments is specified, `savings_plans` and `reservations` can be left to `None`
        savings_plans (Union[None, float, int, np.ndarray], optional): Savings plans commitment per hour or day
        reservations (Union[None, np.ndarray, dict], optional): Reservations levels per families. One per usage columns, or dict with keys same as usage columns
        period (Optional[str], optional): Time period of usage. Defaults to None.
        guid (Optional[List[str]], optional): to implement, column with guids in case of long DataFrame. Defaults to None.

    Raises:
        Exception: Negative reservation not allowed
        Exception: Can't infer the series period

    Returns:
        float: the coverage associated with the usage, prices and input levels of commitments

        the savings plans levels must be the ammount of money spend per time period (hours or days)
    """
    return __general_entries__("coverage", usage, prices, commitments, savings_plans, reservations, period, guid)



def under_utilisation(usage, prices, levels) -> float:
    pass




def __general_entries__(
        action: str,
        usage: Union[pd.DataFrame, np.ndarray],
        prices: Union[dict, list, np.ndarray],
        commitments: Optional[dict]=None,
        savings_plans: Union[None, float, int, np.ndarray]=None,
        reservations: Union[None, np.ndarray, dict]=None,
        period: Optional[str]=None,
        guid: Optional[List[str]]=None) -> float:

    if period is not None:
        assert(period in {'hours', 'hrs', 'H', 'days', 'D', 'd', 'h'})
        changes = {'days' : "D", "hours" : "H", "hrs" : 'H', 'day' : 'D', 'h' : 'H', 'd' : 'D'}
        try:
            period = changes[period.lower()]
        except KeyError:
            raise Exception("Period not in {'hours'|'hrs'|'H'|'days'|'D'|'d'|'h'}")

    # here detect if long or wide DataFrame
    if guid is not None:
        assert(guid in usage.columns)
        usage = pd.pivot_table()

           
    if isinstance(usage, pd.DataFrame):
        X = usage.values.astype(float)
        timespan, n = X.shape
        period = __find_period__(usage)
        usage.index = pd.to_datetime(usage.index).to_pydatetime()
        
    if isinstance(usage, (np.ndarray, np.generic)):
        assert period is not None
        X = usage.astype(float)
        timespan, n = X.shape
  

    if commitments is not None:
        assert isinstance(prices, dict)
        assert isinstance(commitments, dict)

        assert set(prices.keys()).issubset({'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'})
        assert set(commitments.keys()).issubset({'OD', 'RI1Y', 'SP1Y', 'RI3Y', 'SP3Y'})
        assert set(commitments).issubset(set(prices))
        assert 'OD' in prices.keys()

        models = [i for i in prices.keys()]
        match action:
            case "cost":
                return rs.final_cost_or_coverage(
                    X,
                    np.array([prices[i] for i in models]),
                    np.hstack([np.zeros((timespan, 1 + (n - 1) * ('RI' == k[:2]))) + np.array(commitments[k]) for k in models if k in commitments.keys()]), # this syntax is to ensure the same order
                    models,
                    period,
                    True
                )
            case "coverage":
                return rs.final_cost_or_coverage(
                    X,
                    np.array([prices[i] for i in models]),
                    np.hstack([np.zeros((timespan, 1 + (n - 1) * ('RI' == k[:2]))) + np.array(commitments[k]) for k in models if k in commitments.keys()]),
                    models,
                    period,
                    False
                )
    if reservations is None:
        reservations = np.zeros(usage.shape)
    if isinstance(reservations, dict):
        assert isinstance(usage, pd.DataFrame)
        reservations = np.array([reservations.get(guid, 0) for guid in usage.columns])
    else:
        reservations = np.array(reservations)

    match period:
        case 'D':
            reservations *= 24
        case 'H':
            pass
        case _:
            raise Exception("Can't infer time_period, please provide period={'days'|'hours'}")

    match reservations.ndim:
        case 1:
            reservations = np.vstack((reservations, )*timespan)
            assert reservations.shape == usage.shape
        case 2:
            assert reservations.shape == usage.shape
        case _:
            raise Exception("Wrong number of dimensions for reservations")
        
    savings_plans = np.zeros((timespan, 1)) + savings_plans
    levels = np.array(np.hstack((savings_plans, reservations), dtype=np.float64))
    if (levels < 0).any():
        raise Exception("Negative reservation or savings plans not allowed")

    match action:
        case "cost":
            return rs.cost(X, np.array(prices), levels)
        case "coverage":
            return rs.coverage(X, np.array(prices), levels)
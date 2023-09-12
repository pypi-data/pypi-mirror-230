import warnings
import numpy as np
import pandas as pd
import finoptim.rust_as_backend as rs

from typing import List, Optional, Callable, Union, Dict

from finoptim.final_results import FinalResults
from finoptim.validations import __validate__prices__, __find_period__


# IF YOU ARE READING THIS :
# 
# I am so sorry. The fact that the programm needs to account for several
# commitments terms and also for current commitments turned it into this
# unreadable mess.
# If you've opened this file, you probably don't have any other choice,
# so I'll just extend to you my sincere apologies and wish you the best
# combination of luck and courage.
# 
# Timo



def __res_to_final_res__(res, columns, prices, period, horizon) -> FinalResults:
    arangment = pd.DataFrame(res.commitments, index=["savings plans"] + list(columns))

    if len(arangment.columns) == 1:
        horizon = horizon.pop()
        arangment.columns = ("three_years_commitments" if horizon == '3Y' else 'one_year_commitments', )

    p = np.zeros(len(columns) + 1)
    for price in prices.index:
        # print(price[2:])
        if price[:2] == "OD":
            continue
        horizon = 'three_years_commitments' if price[2:] == '3Y' else "one_year_commitments"
        p += np.append(1, prices.loc[price] * (23 * (period == "D") + 1)) * arangment[horizon]

    arangment[f"price_per_{period}"] = p

    fres = FinalResults(
        optimal_arangment=arangment,
        minimum=res.minimum,
        coverage=res.coverage,
        n_iter=res.n_iter,
        convergence=res.convergence
    )
    return fres


def optimise_to_delete(usage: pd.DataFrame,
             prices: Union[Dict, pd.DataFrame, Callable],
             period: Optional[str] = None,
             convergence_detail: Optional[bool] = None,
             n_jobs: Optional[int] = 2) -> FinalResults:
     
    """
    Optimise the levels of reservations and savings plans according to the usage to minimize the cost.
    It is important prices of reservations are always inferior to savings plans prices. Otherwise the problem
    is not convex anymore and there is a risk of not reaching a global minimum.

    Args:
        usage (pd.DataFrame): The usage in hours or days of cloud compute
        prices (Union[Dict, pd.DataFrame, Callable]): A `DataFrame` of prices

            Columns must be the same as usage, and index must be pricing models names in:
            `{'OD'|'RI1Y'|'SP1Y'|'RI3Y'|'SP3Y'}`
   
        convergence_detail (Optional[bool], optional): If `True` return convergence details of the optimisation algorithm,
        such as cost and coverage at every iterations. Defaults to None.
        n_job (int, optional): Number of initialisation for the inertial optimiser. This is also the number of threads used,
         every initialisation running in its own thread. Defaults to 2.
    Raises:
        TypeError: If the entry is not a DataFrame
        Exception: If the time period can't be infered

    Returns:
        FinalResults: The optimal commitments on the time period given in a `FinalResult` object
    """

    pass




def optimise(data: Union[list[pd.DataFrame], pd.DataFrame],
                        prices: Union[Dict, pd.DataFrame, Callable[[str], Dict]],
                        current_commitments: Union[None, Dict, pd.DataFrame] = None,
                        period: Optional[str] = None,
                        convergence_detail: Optional[bool] = None,
                        n_jobs: Optional[int] = 2) -> FinalResults:
    """optimise for the preditions of usage

    Args:
        data (np.ndarray): a three dimensionnal array.
        The first dimension is assumed to be datas, and the last one time ?

        current_prices (Union[Dict, pd.DataFrame, Callable[[str], dict]]): A `DataFrame` of prices

            Columns must be the same as usage, and index must be pricing models names in:
            `{'OD'|'RI1Y'|'SP1Y'|'RI3Y'|'SP3Y'}`

        current_levels (Union[None, Dict, pd.DataFrame], optional): A `DataFrame` of commitment levels

                For every reservations, you must indicate the index of ? and the type of reservations ?
                    `{'RI1Y'|'SP1Y'|'RI3Y'|'SP3Y'}`
        Defaults to None.

    Returns:
        FinalResults: still not sure
    """

    prices = __validate__prices__(prices)
    sps = set([c for c in prices.index if c[:2] == 'SP'])
    if sps:
        correct_order = prices.loc[sps.pop()].div(prices.loc['OD'])
        correct_order = np.argsort(correct_order.values)
    prices = prices.reindex(columns=prices.columns[correct_order])

    if isinstance(data, pd.DataFrame):
        period = __find_period__(data)
        shape, columns, index = data.shape, data.columns, data.index

    if isinstance(data, list):
        assert len(data) > 0
        period = __find_period__(data[0])
        shape, columns, index = data[0].shape, data[0].columns, data[0].index
        data = [d.reindex(columns=d.columns[correct_order]) for d in data]
 

    if period not in {'D', 'H'}:
        raise Exception("Can't infer time_period, please provide period={'days'|'hours'}")
    
    if (current_commitments is not None) and (not set(current_commitments).issubset(set(prices.index))):
        raise Exception("You passed commitments without proving their pricing model")
    


    current_reservations = {"RI1Y" : pd.DataFrame(data=np.zeros(shape), columns=columns),
                            "RI3Y" :  pd.DataFrame(data=np.zeros(shape), columns=columns)}
    current_sps_three_years = np.zeros(len(index))
    current_sps_one_year = np.zeros(len(index))
    possible_guids = set(columns)

    if isinstance(current_commitments, dict):
        for model, values in current_commitments.items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                match model:
                    case 'SP1Y':
                        current_sps_one_year[index <= np.datetime64(value['end_date'])] += value['level']
                    case 'SP3Y':
                        current_sps_three_years[index <= np.datetime64(value['end_date'])] += value['level']
                    case 'RI3Y':
                        guid = value['guid']
                        if guid not in possible_guids:
                            warnings.warn("Careful, you have passed current commitments that are not Savings Plans or projected guids")
                        current_reservations[model].loc[index <= np.datetime64(value['end_date']), guid] += value['level']
                    case 'RI1Y':
                        guid = value['guid']
                        if guid not in possible_guids:
                            warnings.warn("Careful, you have passed current commitments that are not Savings Plans or projected guids")
                        current_reservations[model].loc[index <= np.datetime64(value['end_date']), guid] += value['level']
                    case _:
                        raise Exception(r"Wrong Pricing model. Pricing model must be in {OD|SP1Y|SP3Y|RI1Y|RI3Y}")

                

    if isinstance(current_commitments, pd.DataFrame):
        raise NotImplementedError
        # assert commitments are decreasing in time (doesnt make any sens otherwise)
        if any([t not in possible_values for t in current_commitments.columns]):
            warnings.warn("Careful, you have passed current commitments that are not Savings Plans are projected guids")
        current_commitment_max_date = np.datetime64(current_commitments.index.max())
        for t in current_commitments.columns:
              match t:
                case 'SP1Y':
                    current_sps_one_year[data.index <= current_commitment_max_date] += current_commitments[t]
                case 'SP3Y':
                    current_sps_three_years[data.index <= current_commitment_max_date] += current_commitments[t]
                case _:
                    current_reservations_df.loc[data.index <= current_commitment_max_date, t] += current_commitments[t]

    current_reservations['SP3Y'] = current_sps_three_years[:, np.newaxis]
    current_reservations['SP1Y'] = current_sps_one_year[:, np.newaxis]
    commitments = np.hstack([current_reservations[k] for k in prices.index if k != 'OD'])
    horizon = set([p[-2:] for p in prices.index if p != 'OD'])


    if isinstance(data, list):
        # here assert all dimensions are correct
        assert all([isinstance(l, pd.DataFrame) for l in data])
        values = np.stack([pred.values for pred in data]).astype(float)
        res = rs.optimise_predictions(values, prices.values, commitments, list(prices.index), period, convergence_detail)

    if isinstance(data, pd.DataFrame):
        # careful here, current commitments are not taken into account
        X = data.values.astype(float)
        timespan, n = data.shape
        order = {"RI1Y" : 3, "RI3Y" : 4, "SP1Y" : 1, "SP3Y" : 2, "OD" : 0}
        if len(horizon) == 1:
            # use simplified optimisation to go faster
            print("convex optimisation")
            # here sort the prices accordingly
            prices.sort_index(axis='index', inplace=True, key=lambda x: x.map(order))
            if (np.diff(prices.values, axis=0) > 0).any():
                raise Exception("Prices do not follow the correct order for every instance, optimisation will fail")
            res = rs.simple_optimisation(X, prices.values, period, convergence_detail, step=10)
        else:
            print("inertial optimisation")
            parameters = prices.index.map({"RI1Y" : n, "RI3Y" : n, "SP1Y" : 1, "SP3Y" : 1, "OD" : 0}).values.sum()
            current_levels = np.zeros((timespan, parameters))
            res = rs.general_optimisation(X, prices.values, current_levels, list(prices.index), period, n_jobs, convergence_detail)

    print("FINI")
    return __res_to_final_res__(res, columns, prices, period, horizon)
    

    
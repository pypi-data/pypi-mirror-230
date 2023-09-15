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
# unreadable mess. Trust me it was a nightmare.
# If you've opened this file, you probably don't have any other choice,
# so I'll just extend to you my sincere apologies and wish you the best
# combination of luck and courage.
#
# Timo the intern


def __res_to_final_res__(res, columns, prices, period, horizon, ri_cost) -> FinalResults:
    arangment = pd.DataFrame(res.commitments, index=[
                             "savings plans"] + list(columns))

    if len(arangment.columns) == 1:
        horizon = horizon.pop()
        arangment.columns = (
            "three_years_commitments" if horizon == '3Y' else 'one_year_commitments', )

    p = np.zeros(len(columns) + 1)
    for price in prices.index:
        if price in {"OD", "CurrentSP"}:
            continue
        horizon = 'three_years_commitments' if price[2:
                                                     ] == '3Y' else "one_year_commitments"
        p += np.append(1, prices.loc[price] * (23 *
                       (period == "D") + 1)) * arangment[horizon]

    arangment[f"price_per_{period}"] = p

    fres = FinalResults(
        optimal_arangment=arangment,
        minimum=res.minimum + ri_cost,
        coverage=res.coverage,
        n_iter=res.n_iter,
        convergence=res.convergence
    )
    return fres


def optimise(data: Union[list[pd.DataFrame], pd.DataFrame],
             prices: Union[Dict, pd.DataFrame, Callable[[str], Dict]],
             current_commitments: Optional[List[dict]] = None,
             current_commitments_prices: Union[None, Dict,
                                               pd.DataFrame, Callable[[str], Dict]] = None,
             period: Optional[str] = None,
             convergence_detail: Optional[bool] = False,
             n_jobs: Optional[int] = 2) -> FinalResults:
    """Optimise the commitments for the the given usage. If `data` is a list of usage, the optimisation
    process will minimize the average cost on all the usages.

    Args:
        data (Union[list[pd.DataFrame], pd.DataFrame]):
            `Usage` should be a `pd.DataFrame` with a time index. The usage is per hours or days of cloud compute.

        prices (Union[Dict, pd.DataFrame, Callable[[str], Dict]]):
            A `pd.DataFrame` of prices. Columns must be the same as usage, and index must be pricing models names in:
            `{'OD'|'RI1Y'|'SP1Y'|'RI3Y'|'SP3Y'}`

            If `prices` is a dictionary, it must have as keys the pricing models, and as values the prices as arrays
            or dictionaries.
            It is important prices of reservations are always inferior to savings plans prices. Otherwise the problem
            is not convex anymore and there is a risk of not reaching a global minimum.

        current_commitments (Optional[List[dict]]):
            YOU NEED TO SPECIFY THE PRICES

            example of a valid input : 
            ```python
            from datetime import date

            current_commitments = 
                        [{"type" : "RI3Y", "level" : 5, 'guid' : 'a', "end_date" : date(2000, 12, 21), 'price_key' : 5},
                        {'type' : 'SP6Y', "level" : 1, 'end_date' : date(2006, 10, 4), "price_key" : "SP3Y"},
                        {'type' : 'SP3Y', 'level' : 5, 'end_date' : date(2001, 1, 1), "price_key" : "SP3Y"},
                        {'type' : 'SP3Y', "level" : 4, "end_date" : date(1999, 12, 31), "price_key" : "SP3Y"},
                        {'type' : 'SP3Y', "level" : 4, "end_date" : date(2000, 2, 3), "price_key" : "SP1Y"},
                        {'type' : 'SP3Y', "level" : 4, "end_date" : date(2000, 5, 3), "price_key" : "SP1Y"}]
            ```
            Defaults to None.

        period (Optional[str]):
            The minimum time delta between each row. Defaults to None, because it can be inferred from the data.

        convergence_detail (Optional[bool]):
            Set to `True` if you want the results object to carry informations about the convergence of the optimisation process. Defaults to False.

        n_jobs (Optional[int]):
            Number of initialisation for the inertial optimiser. This is also the number of threads used,
            every initialisation running in its own thread. Defaults to 2.

    Raises:
        Exception: Can't infer time_period, please provide period=`{'days'|'hours'}`
        Exception: You passed commitments without proving their pricing model
        Exception: Prices do not follow the correct order for every instance, optimisation will fail
        NotImplementedError: You can't yet use a function as an argument for `prices`
        Exception: Wrong Pricing model. Pricing model must be in `{OD|SP1Y|SP3Y|RI1Y|RI3Y}`

    Returns:
        FinalResults: The optimal commitments on the time period given in a `FinalResult` object
    """

    prices = __validate__prices__(prices)
    if current_commitments is not None:
        current_commitments_prices = pd.DataFrame(current_commitments_prices)

    sps = set([c for c in prices.index if c[:2] == 'SP'])
    if sps:
        correct_order = prices.loc[sps.pop()].div(prices.loc['OD'])
        correct_order = np.argsort(correct_order.values)
    prices = prices.reindex(columns=prices.columns[correct_order])

    if isinstance(data, pd.DataFrame):
        period = __find_period__(data)
        shape, columns, index = data.shape, data.columns, data.index
        start_date = data.index.min()

    if isinstance(data, list):
        assert len(data) > 0
        period = __find_period__(data[0])
        shape, columns, index = data[0].shape, data[0].columns, data[0].index
        data = [d.reindex(columns=d.columns[correct_order]) for d in data]
        start_date = min([d.index.min() for d in data])

    timespan, n = shape

    if period not in {'D', 'H'}:
        raise Exception(
            "Can't infer time_period, please provide period={'days'|'hours'}")

    current_reservations = pd.DataFrame(data=np.zeros(shape), columns=columns)

    current_sps_three_years = np.zeros(len(index))
    current_sps_one_year = np.zeros(len(index))
    current_sps = dict()
    possible_guids = set(columns)
    ri_cost = 0

    if isinstance(current_commitments, list):
        items_to_have = {'type', 'level', 'end_date', 'price_key'}
        for commitment in current_commitments:
            assert isinstance(commitment, dict)
            assert items_to_have.issubset(set(commitment))
            type, term = commitment['type'][:2], commitment['type'][2:]
            match type:
                case 'RI':
                    assert 'guid' in commitment.keys()
                    assert 'price_key' in commitment.keys()
                    guid = commitment['guid']
                    current_reservations.loc[index <= np.datetime64(
                        commitment['end_date']), guid] += commitment['level']
                    ri_cost += commitment['price_key'] * \
                        current_reservations[guid]
                case "SP":
                    id = commitment['price_key']
                    if id not in current_commitments_prices.index:
                        raise Exception(
                            f"prices for commitment {id} are not specified")
                    tmp = np.zeros((timespan, 1))
                    tmp[index <= np.datetime64(
                        commitment['end_date']), :] = commitment['level']
                    current_sps[id] = current_sps.get(
                        id, np.zeros((timespan, 1))) + tmp

    if isinstance(current_commitments, pd.DataFrame):
        raise NotImplementedError
        # assert commitments are decreasing in time (doesnt make any sens otherwise)
        if any([t not in possible_values for t in current_commitments.columns]):
            warnings.warn(
                "Careful, you have passed current commitments that are not Savings Plans are projected guids")
        current_commitment_max_date = np.datetime64(
            current_commitments.index.max())
        for t in current_commitments.columns:
            match t:
                case 'SP1Y':
                    current_sps_one_year[data.index <=
                                         current_commitment_max_date] += current_commitments[t]
                case 'SP3Y':
                    current_sps_three_years[data.index <=
                                            current_commitment_max_date] += current_commitments[t]
                case _:
                    current_reservations_df.loc[data.index <=
                                                current_commitment_max_date, t] += current_commitments[t]

    horizon = set([p[-2:] for p in prices.index if p != 'OD'])

    # add current sp to the price
    if current_commitments is not None:
        current_sp_commitments = np.hstack([v for v in current_sps.values()])
        for k in current_sps.keys():
            prices.loc["CurrentSP"] = current_commitments_prices.loc[k]
    else:
        current_sp_commitments = np.zeros((0, 0))

    if isinstance(data, list):
        # here assert all dimensions are correct
        assert all([isinstance(l, pd.DataFrame) for l in data])
        values = np.stack([(pred.values - current_reservations.values)
                          for pred in data]).clip(0).astype(float)
        res = rs.optimise_predictions(values, prices.values, current_sp_commitments, list(
            prices.index), period, n_jobs, convergence_detail)

    if isinstance(data, pd.DataFrame):
        # careful here, current commitments are not taken into account
        X = (data.values - current_reservations.values).clip(0).astype(float)
        timespan, n = data.shape
        order = {"RI1Y": 3, "RI3Y": 4, "SP1Y": 1, "SP3Y": 2, "OD": 0}
        if len(horizon) == 1:
            # use simplified optimisation to go faster
            print("convex optimisation")
            # here sort the prices accordingly
            prices.sort_index(axis='index', inplace=True,
                              key=lambda x: x.map(order))
            if (np.diff(prices.values, axis=0) > 0).any():
                raise Exception(
                    "Prices do not follow the correct order for every instance, optimisation will fail")
            res = rs.simple_optimisation(
                X, prices.values, period, convergence_detail, step=10)
        else:
            print("inertial optimisation")
            # parameters = prices.index.map({"RI1Y" : n, "RI3Y" : n, "SP1Y" : 1, "SP3Y" : 1, "OD" : 0}).values.sum()
            # current_levels = np.zeros((timespan, parameters))
            res = rs.general_optimisation(X, prices.values, current_sp_commitments, list(
                prices.index), period, n_jobs, convergence_detail)

    return __res_to_final_res__(res, columns, prices, period, horizon, ri_cost)

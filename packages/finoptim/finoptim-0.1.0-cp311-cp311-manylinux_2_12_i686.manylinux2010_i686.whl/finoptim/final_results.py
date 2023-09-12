import pandas as pd

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class FinalResults:
    """Class for keeping tidy results."""
    optimal_arangment: pd.DataFrame
    minimum: float
    coverage: float
    n_iter: int = 0
    convergence: Optional[List[float]] = None
    formatted: Optional[pd.DataFrame] = None

    def format(self, name_dict: Optional[dict] = None, **kwargs: List[dict]) -> pd.DataFrame:
        """
        ## YOU HAVE TO GIVE NAMED ARGUMENTS !
        
        The name of your argument will be the name of the added column.
        
        Create a new `DataFrame` out of `self.optimal_arangment` with prettier values.
        It is sorted by price, and you can add any columns you want using a dictionnary mapping
        the *guid*s to your wanted values

        Returns:
            pd.DataFrame: prettier DataFrame

        Examples
        --------
        ```python
        res = fp.optimise(df_real, prices_df)
        guid_to_instance_name = {"K7YHHNFGTNN2DP28" : 'i3.large', 'SAHHHV5TXVX4DCTS' : 'r5.large'}
        res.format(instance_type=guid_to_instance_name)
        print(res)
        >>>
        ╭─────────────────┬──────────────────────────┬───────────────╮
        │ instance_type   │  three_year_commitments  │  price_per_D  │
        ├─────────────────┼──────────────────────────┼───────────────┤
        │ i3.large        │           1338           │     2,886     │
        │ r5.large        │           1570           │     2,564     │
        │ savings plans   │           1937           │     1,937     │
        ╰─────────────────┴──────────────────────────┴───────────────╯
        ```
        """
        res = self.optimal_arangment
        price_col, rest = res.columns[-1], res.columns[:-1]
        md = res.loc[res[price_col] != 0].drop_duplicates().sort_values(by=price_col, ascending=False)

        # for k, mapping in name_dict.items():
        #     md[k] = md.index.map(mapping)
        # md = md[list(kwargs) + list(rest) + [price_col]]

        for k, mapping in kwargs.items():
            md[k] = md.index.map(mapping)
        md = md[list(kwargs) + list(rest) + [price_col]]
        self.formatted = md
        return md

    def __repr__(self) -> str:
        if self.formatted is None:
            return f"minimum : {self.minimum}, coverage : {self.coverage}"
        return self.formatted.to_markdown(index=False, tablefmt='rounded_outline', floatfmt=',.0f', numalign='center')
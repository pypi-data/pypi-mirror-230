from typing import Callable, List

import pandas as pd


def support_groups(f: Callable) -> Callable:
    """
    If a function can be applied to a DataFrame or a DataFrameGroupBy then it will
    require different syntax for both cases. This decorator provides an abstraction
    that hides logic related to grouping operation. It lets you run a function
    seamlessly on a DataFrame and grouped DataFrame depending on whether the
    "group_columns" parameter was provided or not.
    """
    def _f(
        df: pd.DataFrame,
        group_columns: List[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        if group_columns:
            groups = df.groupby(by=group_columns, group_keys=False)
            df = groups.apply(func=f, **kwargs)
        else:
            df = f(df, **kwargs)
        return df
    return _f

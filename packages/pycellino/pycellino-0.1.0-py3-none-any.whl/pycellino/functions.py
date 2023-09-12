from typing import Dict, List

import pandas as pd


def group_feature_values(
    df: pd.DataFrame,
    index: List[str],
    feature_name: str,
    feature_groups: Dict[str, List[str]],
) -> pd.DataFrame:
    dfs = []
    for feature_values_label, feature_values in feature_groups.items():
        local_df = _build_feature_values_group(
            df=df,
            index=index,
            feature_name=feature_name,
            feature_values=feature_values,
            feature_values_label=feature_values_label)
        dfs.append(local_df)
    df = pd.concat(objs=dfs, ignore_index=True)
    return df


def _build_feature_values_group(
    df: pd.DataFrame,
    index: List[str],
    feature_name: str,
    feature_values: List[str],
    feature_values_label: str
) -> pd.DataFrame:
    mask = df[feature_name].isin(feature_values)
    df = df[mask]
    df = df.groupby(
        by=index,
        dropna=False,
        observed=True,
        group_keys=False
    ).sum(numeric_only=True).reset_index()
    df[feature_name] = feature_values_label
    return df

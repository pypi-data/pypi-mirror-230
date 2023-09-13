import numpy as np
import pandas as pd
from typing import Union, Callable, Iterable, Any
from functools import partial

DF = pd.DataFrame
def dfat(df: DF, index, col, default=None):
    """

    similar to df.at[idx, col] but returns None instead of throwing
    """
    try:
        res = df.at[index, col]
        if pd.isnull(res):
            return default
        return res
    except (ValueError, KeyError):
        return default


def get_duplicates(primary_key: list, df: DF,
                   report_cols: str | list
                   ) -> DF:
    """
    groups duplicates by primary key (PK) displaying all additional report_cols
    """
    dup = df[df[pk].duplicated(keep=False)]
    grouped = dup.groupby(pk)[report_cols].apply(set)
    return grouped

def hconcat_exc(df1: DF, df2: DF) -> DF:
    cols = [c for c in df2.columns if c not in df1.columns]
    res = df1.join(df2[cols])
    return res

def get_at_level(df: DF, level: int, key: str) -> DF:
    return df.loc[:,
        df.columns.get_level_values(level) == key
    ].droplevel(level, axis=1)

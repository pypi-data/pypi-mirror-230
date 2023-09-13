from __future__ import annotations

import logging
from typing import Union, Callable
import pandas as pd
import polars as pl
from polars import all, DataFrame as DF

from polarmints.core import PolarsBase

logger = logging.getLogger(__name__)

class PandasMirrorSeries(PolarsBase):
    @property
    def index(self):
        return getattr(self._df, 'index', [])

    @property
    def pd(self):
        res = self._df.to_pandas()
        if self.index:
            res.set_index(self.index, inplace=True)
        return res

    def ffill(self) -> DF:
        return self._df.fill_null(strategy='forward')
    def bfill(self) -> DF:
        return self._df.fill_null(strategy='backward')

    def zscore(self, ddof=0) -> DF:
        df = self._df
        return (df - df.mean()) / df.std(ddof=ddof)


class PandasMirror(PandasMirrorSeries):

    # Overridden
    def zscore(self, *args, **kwargs) -> DF:
        return self._df.select(all().pd.zscore(*args, **kwargs))


######################## syntax sugar for all other pandas funcs ########################
def replace_func(func_name: str) -> Callable:
    def inner(self, *args, **kwargs):
        pddf = getattr(self.pd, func_name)(*args, **kwargs)
        if self.index:
            pddf.reset_index(inplace=True)
        if isinstance(pddf, (pd.DataFrame, pd.Series)):
            return pl.from_pandas(pddf)
        return pddf
    return inner

for pd_cls, pl_cls in {
    pd.Series: PandasMirrorSeries,
    pd.DataFrame: PandasMirror,
}.items():
    for name in dir(pd_cls):
        if not hasattr(pl_cls, name) and callable(getattr(pd_cls, name)):
            setattr(pl_cls, name, replace_func(name))
            # print(f'setting {name} onto {pl_cls}')
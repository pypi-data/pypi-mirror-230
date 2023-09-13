from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Union, Callable
import polars as pl
from polars import exclude, Series, DataFrame as DF
from polarmints.sugar import c

logger = logging.getLogger(__name__)

LIST_OR_STR_TYPE = str | list[str]

class PolarsBase:
    def __init__(self, df: DF):
        self._df = df




class PolarMints(PolarsBase):

    def get(self, col: str, default=None) -> Series:
        if col in self._df:
            return self._df[col]
        return default

    def filter_dict(self, pred: dict) -> DF:
        return self._df.filter(dict2pred(pred))

    def todict(self, key: LIST_OR_STR_TYPE, val: LIST_OR_STR_TYPE) -> dict:
        kvpair = [self._df.select(
            (c[v] if isinstance(v, str) else pl.coalesce(v))
        ).to_series() for v in (key, val)]
        return dict(zip(*kvpair))

    def replace_pred(self, *pairs, cols=pl.all()) -> DF:
        """
        Experimental TODO: must be a betterway
        """
        res = self._df.with_columns(where(
            pairs + [(None, cols)]
        ).keep_name())
        return res

    def safe_rename(self, mapping: dict) -> DF:
        excs = [v for k, v in mapping.items() if k != v]
        return self._df.select(exclude(excs)
        ).rename(mapping)

    def with_cols(self, inputs: list[Union[list, dict]]) -> DF:
        res = self._df
        for args in inputs:
            res = res.with_columns(**args) if isinstance(args, dict) else res.with_columns(args)
        return res

    def join(self, other: DF, on: str | Sequence[str], *args, **kwargs):
        """
        infers type of on columns and casts other df to match
        """
        if isinstance(on, str):
            on = [on]
        other_cast = other.with_columns([
            c[col].cast(self._df[col].dtype)
        for col in on])
        return self._df.join(other_cast, on, *args, **kwargs)

    def convert_schema(self, schema: dict, strict=False) -> DF:
        """
        convert schema to polars schema
        """
        fn = self._df.select if strict else self._df.with_columns
        return fn(
            c[col].cast(dtype) for col, dtype in schema.items() if strict or col in self._df.columns
        )

    def renamefn(self, fn: Callable) -> DF:
        return self._df.rename({k: fn(k) for k in self._df.columns})

    ######################## Convenience Shortcuts #####################


    def tsc(self, samplesize=100000):
        df = self._df
        if len(df) > samplesize:
            print(f'truncating {len(df)} rows to {samplesize}')
            df = df.sample(samplesize)
        df.to_pandas().to_clipboard(index=False)


    @property
    def tc(self):
        self.tsc()

####################### MAIN examples #######################

if __name__ == '__main__':
    dfpl = pl.DataFrame({'a': [1, 2, 3]})
    c = PolarsCol()
    expr = c.a == 1
    expr2 = c['a'] > 2
    filtered = dfpl.filter(expr | expr2)

    dfs = {
        'd1': pl.DataFrame({
            'd': [1, 2, 3],
            'a': [1, 2, 3],
            'b': [1, 2, 3],
            'c': [1, 2, 3],
        }),
        'd2': pl.DataFrame({
            'd': [1, 2, 3],
            'a': [2, 2, 2],
            'c': [2, 2, 2],
        }),
        'd3': pl.DataFrame({
            'a': [3, 2, 1],
            'b': [3, 2, 1],
        }),
    }
    combined = combine_struct(dfs, ['d'])

    df = dfs['d1']
    df.index = ['a', 'b']
    res = df.pd.replace({1: 11})

    df['a'].pd.abs()



import pandas as pd
import numpy as np
import polars as pl
import pandas_market_calendars as mcal
from datetime import date

BUSDAY_TYPES = pl.DataFrame | pl.Series | pd.DataFrame | pd.Series

def _busday_offset(dates: BUSDAY_TYPES, offsets, cal_name: str = None, **kwargs) -> pl.Series:
    if cal_name:
        kwargs['holidays'] = mcal.get_calendar(cal_name).holidays().holidays
    kwargs['roll'] = kwargs.get('roll', 'forward')
    res = np.busday_offset(dates, offsets, **kwargs)
    return res

def busday_offset(dates: BUSDAY_TYPES, *args, **kwargs) -> pl.Series:
    res = _busday_offset(dates, *args, **kwargs)
    match type(dates):
        case pl.DataFrame:
            df = pl.from_numpy(res)
            df.columns = dates.columns
            return df
        case pd.DataFrame:
            return pd.DataFrame(res, dates.columns)
        case pl.Series:
            return pl.from_numpy(res).to_series()
        case pd.Series:
            return pd.Series(res)
        case _:
            return res


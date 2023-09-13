import polars as pl
from polars import Expr, LazyFrame, Series

from polarmints.core import PolarMints
from polarmints.pandas_mirror import PandasMirrorSeries, PandasMirror
from polarmints.sugar import c
DF = pl.DataFrame

FRAMES = [DF, LazyFrame]
def create_namespaces(name: str, ns_class: type, clss: list = None):
    for cls in clss or [Expr, LazyFrame, DF, Series]:
        pl.api._create_namespace(name, cls)(ns_class)


create_namespaces('pd', PandasMirrorSeries, [Series])
create_namespaces('pd', PandasMirror, [DF])
for name, clss in {
    'pm':  PolarMints,
}.items():
    create_namespaces(name, clss, FRAMES)
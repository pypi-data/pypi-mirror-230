"""Model several financial assets."""

from vistafetch.model.asset.financial_data import PriceData
from vistafetch.model.asset.bond import Bond
from vistafetch.model.asset.fund import Fund
from vistafetch.model.asset.index import Index
from vistafetch.model.asset.metal import PreciousMetal
from vistafetch.model.asset.stock import Stock

__all__ = [
    "Bond",
    "Fund",
    "Index",
    "PreciousMetal",
    "PriceData",
    "Stock",
]

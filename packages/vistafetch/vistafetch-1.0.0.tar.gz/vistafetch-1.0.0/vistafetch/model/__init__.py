"""Collection of model classes.

All model classes are defined using Pydantic.
"""
from vistafetch.model.asset import Bond, Fund, Index, PreciousMetal, Stock
from vistafetch.model.search_result import SearchResult

__all__ = [
    "Bond",
    "Fund",
    "Index",
    "PreciousMetal",
    "Stock",
    "SearchResult",
]

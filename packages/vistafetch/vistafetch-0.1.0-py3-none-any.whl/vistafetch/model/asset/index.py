"""Model an index."""
from typing import Literal

from vistafetch.model.asset.financial_asset import FinancialAsset
from vistafetch.model.asset.financial_asset_type import FinancialAssetType

__all__ = [
    "Index",
]


class Index(FinancialAsset):
    """Models an investment index within the scope of this library.

    A stock index is a measurement of the stock market that tracks
    the performance of a group of stocks or other assets.

    """

    _type = FinancialAssetType.INDEX

    entity_type: Literal[_type.value]  # type: ignore

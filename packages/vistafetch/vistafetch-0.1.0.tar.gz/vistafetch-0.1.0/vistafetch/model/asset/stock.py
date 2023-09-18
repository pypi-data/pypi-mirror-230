"""Model a stock."""
from typing import Literal

from vistafetch.model.asset.financial_asset import FinancialAsset
from vistafetch.model.asset.financial_asset_type import FinancialAssetType

__all__ = [
    "Stock",
]


class Stock(FinancialAsset):
    """Models a stock within the scope of this library.

    A stock is a type of investment that represents ownership in a company.
    When one buys a stock, one is purchasing a small piece of
        that company, called a share.

    """

    _type = FinancialAssetType.STOCK

    entity_type: Literal[_type.value]  # type: ignore

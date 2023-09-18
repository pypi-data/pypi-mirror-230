"""Model a fund."""
from typing import Literal

from vistafetch.model.asset.financial_asset import FinancialAsset
from vistafetch.model.asset.financial_asset_type import FinancialAssetType

__all__ = [
    "Fund",
]


class Fund(FinancialAsset):
    """Models an investment fund within the scope of this library.

    An investment fund is a financial product that pools money
    from multiple investors to buy a diversified portfolio of
    assets, such as stocks, bonds, real estate, and commodities.
    This comprises various types of investment funds,
    including mutual funds, exchange-traded funds (ETFs),
    and hedge funds, each with its own investment strategy and risk profile.

    """

    _type = FinancialAssetType.FUND

    entity_type: Literal[_type.value]  # type: ignore

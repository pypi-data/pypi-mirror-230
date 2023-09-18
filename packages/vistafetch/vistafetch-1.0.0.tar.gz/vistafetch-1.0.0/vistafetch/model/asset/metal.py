"""Model a precious metal."""
from typing import Literal

from vistafetch.model.asset.financial_asset import FinancialAsset
from vistafetch.model.asset.financial_asset_type import FinancialAssetType

__all__ = [
    "PreciousMetal",
]


class PreciousMetal(FinancialAsset):
    """Models an investment index within the scope of this library.

    A precious metal is a rare metallic element that has high economic value
    due to various factors, including their scarcity, use in industrial processes,
    hedge against currency inflation, and role throughout history as a store of value.

    """

    _type = FinancialAssetType.METAL

    entity_type: Literal[_type.value]  # type: ignore

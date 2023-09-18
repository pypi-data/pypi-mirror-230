"""Model a bond."""
from typing import Literal

from vistafetch.model.asset.financial_asset import FinancialAsset
from vistafetch.model.asset.financial_asset_type import FinancialAssetType

__all__ = [
    "Bond",
]


class Bond(FinancialAsset):
    """Models a bond within the scope of this library.

    A bond is a type of debt security that represents
    a loan made by an investor to a borrower,
    such as a government or corporation.
    When an investor buys a bond, they are essentially lending money to
    the issuer for a specified period of time,
    during which the issuer promises to pay the investor a fixed rate of interest.

    """

    _type = FinancialAssetType.BOND

    entity_type: Literal[_type.value]  # type: ignore

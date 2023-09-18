"""Model a financial asset in the context of this library."""
from abc import ABC
from functools import cached_property
from typing import Literal

from requests import HTTPError

from vistafetch.constants import ONVISTA_API_BASE_URL
from vistafetch.model.asset import PriceData
from vistafetch.model.asset.financial_asset_type import FinancialAssetType
from vistafetch.model.base import VistaEntity
from vistafetch.session import api_session

__all__ = [
    "FinancialAsset",
]


class FinancialAsset(VistaEntity, ABC):
    """General description of a financial asset in the context of this library.

    This class models the shared attributes of a financial asset as
    returned from the API.cThese attributes are not comprehensive,
    it's currently only a selection of the most important ones.
    Thus, they may get extended in the future.

    Please note, that this class is only intended to serve as
    an abstract base class.The concrete financial assets as
    returned by the API still need to be defined. Thereby,
    it is required to overwrite the attribute `_type` accordingly.

    Attributes
    ----------
    display_type: display name of the asset type
    entity_type: name of the entity type as determined by the API,
        use values of `FinancialAssetType`
    isin: ISIN code of the asset
        (An International Securities Identification Number (ISIN)
        is a code that uniquely identifies a security globally
        for the purposes of facilitating clearing, reporting,
        and settlement of trades.)
    name: full name of the financial asset
    tiny_name: short name of the financial asset, preferably useful as display name
    wkn: WKN code of the financial asset (The 'Wertpapierkennnummer' (WKN) is a
        German securities identification code.)

    """

    _type: FinancialAssetType = FinancialAssetType.UNKNOWN

    display_type: str
    entity_type: Literal[_type.value]  # type: ignore
    isin: str
    name: str
    tiny_name: str
    wkn: str

    def __query_price_data(self) -> PriceData:
        if self._type == FinancialAssetType.UNKNOWN:
            raise NotImplementedError(
                "`price_data` is called directly on the "
                "abstract class `Financial Asset`. "
                "Please use a valid financial asset class."
            )
        response = api_session.get(
            f"{ONVISTA_API_BASE_URL}{self._type.value.lower()}s/ISIN:{self.isin}/snapshot"
        )
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise RuntimeError(f"API does not return a valid response: {e}")

        response_dict = response.json()
        if "quote" not in response_dict.keys():
            raise ValueError(
                f"API response does not contain expected data: {response_dict}"
            )

        return PriceData.model_validate(response_dict["quote"])

    @cached_property
    def price_data(self) -> PriceData:
        """Get the price data available for this financial asset."""
        return self.__query_price_data()

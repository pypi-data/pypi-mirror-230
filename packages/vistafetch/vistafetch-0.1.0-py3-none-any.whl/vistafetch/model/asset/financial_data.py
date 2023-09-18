"""Model financial information in the context of this library."""
from datetime import datetime

from pydantic import Field, field_validator

from vistafetch.constants import ONVISTA_API_TIMEZONE
from vistafetch.model.base import VistaEntity

__all__ = [
    "PriceData",
]


class PriceData(VistaEntity):
    """Price data of a financial asset.

    This class models price-related data of a financial asset.
    Alongside the currency, it provides different price parameters and
    the corresponding timestamp of measurement.

    Attributes
    ----------
        currency_symbol: symbol of the corresponding currency,
            in ISO notation as returned by the API, e.g., 'EUR'.
        datetime_high: timestamp of measurement for price value `high`, timezone-aware
        datetime_last: timestamp of measurement for price value `last`, timezone-aware
        datetime_low: timestamp of measurement for price value `low`, timezone-aware
        datetime_open: timestamp of measurement for price value `open`,
            timezone-aware
        high: The highest price at which the stock was traded during
            the day's trading session.
        low: The lowest price at which the stock was traded during
            the day's trading session.
        last: The last price at which the stock was traded before
            the market closed.
            This is also known as the closing price.
        open: The price at which the stock began trading at
            the beginning of the day's trading session.

    """

    currency_symbol: str = Field(alias="isoCurrency")
    datetime_high: datetime
    datetime_last: datetime
    datetime_low: datetime
    datetime_open: datetime
    high: float
    last: float
    low: float
    open: float

    @field_validator("datetime_high", "datetime_last", "datetime_low", "datetime_open")
    @classmethod
    def __ensure_timezone_awareness(cls, dt: datetime) -> datetime:
        if not isinstance(dt, datetime):
            raise ValueError(f"{dt} is not a datetime instance.")
        return dt.replace(tzinfo=ONVISTA_API_TIMEZONE)

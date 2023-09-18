"""Constant variables relevant throughout the entire library.

Attributes
----------
ONVISTA_API_BASE_URL: base URL of the Onvista API
ONVISTA_API_TIMEZONE: datetime timezone that is used by the API

"""

from datetime import timezone

__all__ = ["ONVISTA_API_BASE_URL", "ONVISTA_API_TIMEZONE"]

ONVISTA_API_BASE_URL = "https://api.onvista.de/api/v1/"
ONVISTA_API_TIMEZONE = timezone.utc

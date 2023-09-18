"""Client to fetch Onvista API."""
import logging
from typing import Dict, Optional

from vistafetch.logs import set_up_logging
from requests import HTTPError

from vistafetch.constants import ONVISTA_API_BASE_URL
from vistafetch.session import api_session
from vistafetch.model import SearchResult

__all__ = [
    "VistaFetchClient",
]

logger = logging.getLogger(name=__name__)


class VistaFetchClient:
    """Client to fetch financial data from the Onvista API.

    Args:
    ----
        client_headers: additional headers to be sent with every request, optional
    """

    def __init__(self, client_headers: Optional[Dict[str, str]] = None):
        set_up_logging()

        http_headers = {"Application": "application/json; charset=utf-8"}

        if client_headers:
            http_headers.update(client_headers)

        # set up a requests session
        # this allows to centrally determine the behavior of all requests made
        api_session.headers.update(http_headers)

        logger.debug(
            "Requests session has been configured with the following headers: \n"
            f"{http_headers}"
        )
        logger.info("Client has been initialized successfully.")

    @staticmethod
    def search_asset(
        search_term: str,
        max_candidates: Optional[int] = 5,
    ) -> SearchResult:
        """Search for a financial asset.

        Allow to search for specific financial assets.
        Search terms can be (parts of) the asset name, the ISIN, WKN, etc.

        Args:
        ----
        search_term: str
            the term to searched for
        max_candidates: Optional[int]
            maximum amount of returned assets

        Returns:
        -------
            SearchResult

        """
        response = api_session.get(
            f"{ONVISTA_API_BASE_URL}instruments/query?limit={max_candidates}&searchValue={search_term}"
        )
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise RuntimeError(f"API does not return a valid response: {e}")
        logger.debug(f"Response retrieved from the API: {response.json()}")

        return SearchResult.model_validate(response.json())

"""Search result as returned by the API when querying a financial asset."""
from datetime import datetime
from typing import List, Union

from pydantic import Field
from rich.console import Console
from rich.table import Table

from vistafetch.model.asset import Bond, Fund, Index, PreciousMetal, Stock
from vistafetch.model.asset.financial_asset import FinancialAsset
from vistafetch.model.base import VistaEntity

__all__ = [
    "SearchResult",
]


class SearchResult(VistaEntity):
    """Search result as returned by the API.

    This represents the return when searching for a financial asset via the API.

    Attributes
    ----------
        expires: timestamp until the search result is considered to be valid by the API.
        assets: list of financial assets that match the search term
        search_value: the actual value that has been searched for

    """

    expires: datetime
    assets: List[Union[Bond, Fund, Index, PreciousMetal, Stock]] = Field(
        alias="list", discriminator="entity_type"
    )
    search_value: str

    def get(self, index: int = 0) -> FinancialAsset:
        """Get a dedicated financial asset from the result.

        By default, the asset with index '0' is returned.

        Args:
        ----
        index: index of the asset to be returned, default: 0

        Returns:
        -------
        FinancialAsset

        Raises:
        ------
        AttributeError: in case the given index is not available
        RuntimeError: in case the search didn't return any match

        """
        if len(self.assets) == 0:
            raise RuntimeError(
                f"No results found for search term '{self.search_value}'"
            )
        try:
            return self.assets[index]
        except IndexError as e:
            raise AttributeError(
                f"The given index '{index}' is not available. "
                f"Maximum available index: '{len(self.assets)}'"
            ) from e

    def visualize(self) -> None:
        """Visualize the search result in the console.

        Returns
        -------
            None
        """
        console = Console()

        table = Table(title="Financial assets discovered")

        table.add_column("Index", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Asset Type", justify="center")
        table.add_column("ISIN", justify="center")

        for idx, asset in enumerate(self.assets):
            table.add_row(str(idx), asset.tiny_name, asset.entity_type, asset.isin)

        console.print(table)

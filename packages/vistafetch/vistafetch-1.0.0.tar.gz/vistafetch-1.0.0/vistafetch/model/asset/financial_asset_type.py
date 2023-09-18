"""Models the supported types of financial assets."""

from enum import Enum


class FinancialAssetType(Enum):
    """Possible types of financial asset types.

    Attributes
    ----------
        BOND: A debt security that represents a loan made by
            an investor to a borrower.
        FUND: An investment fund, e.g., mutual fund, ETF, etc.
        INDEX: A basket of securities representing a particular market or
            a segment of it.
        STOCK: Share of a corporation or company.
        UNKNOWN: Unknown type of financial asset.
            Should only be used for abstract modeling.

    """

    BOND = "BOND"
    FUND = "FUND"
    INDEX = "INDEX"
    METAL = "PRECIOUS_METAL"
    STOCK = "STOCK"
    UNKNOWN = None

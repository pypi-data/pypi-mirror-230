"""Configure logging for library."""
import logging

from rich.logging import RichHandler

__all__ = [
    "set_up_logging",
]


def set_up_logging() -> None:
    """Configure logging."""
    log_format = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=log_format, datefmt="[%X]", handlers=[RichHandler()]
    )

    logging.debug("Logging set up successfully.")

"""Requests session to be commonly shared.

Attributes
----------
api_session: Session to communicate with the API

"""

from requests import Session

__all__ = [
    "api_session",
]


api_session = Session()

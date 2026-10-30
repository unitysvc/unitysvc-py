"""A client library for accessing Isolated PR2808 review Customer API"""

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)

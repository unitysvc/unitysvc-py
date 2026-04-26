"""UnitySVC Python SDK — customer-facing tools for UnitySVC.

This package provides:

- The :class:`Client` / :class:`AsyncClient` HTTP SDK targeting the
  customer-tagged ``/v1/customer/*`` endpoints: groups, services,
  enrollments, aliases, secrets, recurrent requests, and the
  ``resolve`` dry-run primitive.
- The ``usvc`` CLI for managing the same resources from the terminal.

Quick start::

    from unitysvc import Client

    client = Client(api_key="svcpass_...")

    # Discover: group → service
    llm = client.groups.get_by_name("llm")
    services = client.groups.services(llm.id)

    # Dispatch one-shot
    svc = services.data[0]
    resp = client.services.dispatch(svc.id, json={"messages": [...]})

    # Or at the group level (gateway picks a member service):
    resp = client.groups.dispatch(llm.id, json={"messages": [...]})

The customer context is encoded entirely in the API key, so no
separate ``customer_id`` is required. The default base URL points at
production (``https://api.unitysvc.com``); override with the
``base_url`` constructor argument or the ``UNITYSVC_API_URL`` env var.
"""

from .aclient import AsyncClient
from .client import (
    DEFAULT_API_URL,
    ENV_API_BASE_URL,
    ENV_API_KEY,
    ENV_API_URL,
    ENV_S3_BASE_URL,
    ENV_SMTP_BASE_URL,
    Client,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    UnitysvcSDKError,
    ValidationError,
)

__author__ = """Bo Peng"""
__email__ = "bo.peng@unitysvc.com"

__all__ = [
    # Client
    "Client",
    "AsyncClient",
    "DEFAULT_API_URL",
    "ENV_API_KEY",
    "ENV_API_URL",
    "ENV_API_BASE_URL",
    "ENV_S3_BASE_URL",
    "ENV_SMTP_BASE_URL",
    # Exceptions
    "UnitysvcSDKError",
    "APIError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
]

# API Reference (auto-generated)

This page is auto-generated from source docstrings via
[mkdocstrings](https://mkdocstrings.github.io/). For narrative
documentation with examples, see [SDK Reference](sdk-reference.md).

## Client

::: unitysvc.Client
    options:
      members:
        - from_env
        - secrets
        - aliases
        - recurrent_requests

## AsyncClient

::: unitysvc.AsyncClient
    options:
      members:
        - from_env
        - secrets
        - aliases
        - recurrent_requests

## Resources

### SecretsResource

::: unitysvc.resources.secrets.SecretsResource
    options:
      show_root_heading: true

### AliasesResource

::: unitysvc.resources.aliases.AliasesResource
    options:
      show_root_heading: true

### RecurrentRequestsResource

::: unitysvc.resources.recurrent_requests.RecurrentRequestsResource
    options:
      show_root_heading: true

## Exceptions

::: unitysvc.exceptions
    options:
      members:
        - UnitysvcSDKError
        - APIError
        - AuthenticationError
        - PermissionError
        - NotFoundError
        - ValidationError
        - ConflictError
        - RateLimitError
        - ServerError

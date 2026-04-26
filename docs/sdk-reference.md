# SDK Reference (auto-generated)

This page is auto-generated from source docstrings via
[mkdocstrings](https://mkdocstrings.github.io/). For narrative
documentation with examples, see the [SDK Guide](sdk-guide.md).

## Client

::: unitysvc.Client
    options:
      members:
        - from_env
        - groups
        - services
        - enrollments
        - resolve
        - secrets
        - aliases
        - recurrent_requests

## AsyncClient

::: unitysvc.AsyncClient
    options:
      members:
        - from_env
        - groups
        - services
        - enrollments
        - resolve
        - secrets
        - aliases
        - recurrent_requests

## Resources

### Groups

::: unitysvc.groups.Groups
    options:
      show_root_heading: true

### Services

::: unitysvc.services.Services
    options:
      show_root_heading: true

### Enrollments

::: unitysvc.enrollments.Enrollments
    options:
      show_root_heading: true

### Secrets

::: unitysvc.secrets.Secrets
    options:
      show_root_heading: true

### Aliases

::: unitysvc.aliases.Aliases
    options:
      show_root_heading: true

### RecurrentRequests

::: unitysvc.recurrent_requests.RecurrentRequests
    options:
      show_root_heading: true

### Resolve (dry-run primitive)

::: unitysvc.resolve
    options:
      members:
        - resolve

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

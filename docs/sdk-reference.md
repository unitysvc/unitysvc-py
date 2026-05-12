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
        - request_logs

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
        - request_logs

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

### RequestLogs

::: unitysvc.request_logs.RequestLogs
    options:
      show_root_heading: true

### Streaming responses

`Services.stream()` / `Groups.stream()` (and async siblings) return
these context-managed wrappers. See the [Streaming
section](sdk-guide.md#streaming-responses-sse-ndjson) of the SDK
guide for usage.

::: unitysvc._streaming
    options:
      members:
        - StreamEvent
        - StreamingResponse
        - AsyncStreamingResponse
      show_root_heading: false

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

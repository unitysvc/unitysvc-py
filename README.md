# unitysvc-py

Customer-facing Python SDK and `usvc` CLI for [UnitySVC](https://unitysvc.com/).

This package is a thin, typed facade over the UnitySVC customer API.
It exposes:

- A sync [`Client`](#programmatic-usage) and async `AsyncClient` for
  the customer-tagged backend endpoints.
- The `usvc` CLI for managing the same resources from the terminal.

> **Status:** early scaffolding. The customer API currently exposes
> only a handful of endpoints (aliases, recurrent requests, secrets);
> the SDK tracks those today and will grow as the backend adds more.

## Install

```bash
pip install unitysvc-py
```

## Programmatic usage

```python
from unitysvc_py import Client

client = Client(api_key="svcpass_...")  # or Client.from_env()

# List and set secrets
secrets = client.secrets.list()
for s in secrets.data:
    print(s.name, s.id)

client.secrets.create({"name": "openai-key", "value": "sk-..."})
```

### Configuration

The SDK is configured via a small set of environment variables. Only
`UNITYSVC_API_KEY` is required; everything else has a sensible
default.

| Variable                 | Purpose                                     | Default                                      |
|--------------------------|---------------------------------------------|----------------------------------------------|
| `UNITYSVC_API_KEY`       | Customer API key (`svcpass_...`)            | (required)                                   |
| `UNITYSVC_API_URL`       | Control-plane API base URL                  | `https://api.staging.unitysvc.com/v1`   |
| `UNITYSVC_API_BASE_URL`  | HTTP API gateway base URL (inference)       | (unset)                                      |
| `UNITYSVC_S3_BASE_URL`   | S3-compatible gateway base URL              | (unset)                                      |
| `UNITYSVC_SMTP_BASE_URL` | SMTP gateway base URL                       | (unset)                                      |

The customer context is encoded entirely in the API key, so no
separate `customer_id` argument is required.

`UNITYSVC_API_URL` is what the SDK itself uses for control-plane
calls. The `*_BASE_URL` variables are exposed on `Client` as
`client.api_base_url`, `client.s3_base_url`, `client.smtp_base_url`
for downstream inference/storage/email SDKs to pick up — the SDK
itself doesn't talk to them directly.

### Async client

```python
import asyncio
from unitysvc_py import AsyncClient

async def main():
    async with AsyncClient(api_key="svcpass_...") as client:
        secrets = await client.secrets.list()
        for s in secrets.data:
            print(s.name)

asyncio.run(main())
```

### Errors

All errors are subclasses of `unitysvc_py.UnitysvcSDKError`:

```python
from unitysvc_py import (
    UnitysvcSDKError,
    AuthenticationError,   # 401
    PermissionError,       # 403
    NotFoundError,         # 404
    ValidationError,       # 400, 422
    ConflictError,         # 409
    RateLimitError,        # 429
    ServerError,           # 5xx
    APIError,              # base for everything above
)
```

## CLI: `usvc`

The CLI follows the SDK's configuration — set `UNITYSVC_API_KEY` (and
optionally `UNITYSVC_API_URL`) and you can run:

```
usvc env                              # show which env vars the SDK will pick up

# Secrets
usvc secrets list                     # list secrets
usvc secrets set NAME --value V       # create or update a secret by name
usvc secrets delete NAME              # delete a secret by name

# Service aliases
usvc aliases list
usvc aliases show ALIAS_ID
usvc aliases delete ALIAS_ID

# Recurrent requests
usvc recurrent-requests list
usvc recurrent-requests show REQUEST_ID
usvc recurrent-requests trigger REQUEST_ID
usvc recurrent-requests delete REQUEST_ID
```

Every command accepts `--api-key` and `--base-url` overrides.

## Layout

```
src/unitysvc_py/
├── client.py          # Client (sync) facade
├── aclient.py         # AsyncClient (async) facade
├── exceptions.py      # UnitysvcSDKError + status-code subclasses
├── _http.py           # internal: unwrap generated Response → typed model or APIError
├── resources/
│   ├── secrets.py             # client.secrets.*
│   ├── aliases.py             # client.aliases.*
│   ├── recurrent_requests.py  # client.recurrent_requests.*
│   ├── asecrets.py            # async mirror
│   ├── aaliases.py            # async mirror
│   └── arecurrent_requests.py # async mirror
├── _generated/        # openapi-python-client output (do not edit by hand)
├── commands/          # Typer command groups for the CLI
│   ├── _helpers.py    #   run_async, async_client, model_list, ...
│   └── secrets.py     #   `usvc secrets {list,set,delete}`
└── cli.py             # `usvc` Typer entry point
```

## Regenerating the API client

The low-level client under `src/unitysvc_py/_generated/` is produced
by [openapi-python-client] from a copy of the backend OpenAPI spec at
`openapi.json`. To regenerate after a backend change:

```bash
# Requires a sibling checkout of unitysvc/unitysvc
./scripts/generate_client.sh
```

The script reads `../unitysvc/backend/generated/customer_api.json` by
default; pass an explicit spec path as the first argument to override.

[openapi-python-client]: https://github.com/openapi-generators/openapi-python-client

## License

MIT

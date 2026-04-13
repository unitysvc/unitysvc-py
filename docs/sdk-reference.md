# SDK Reference

`unitysvc-py` ships sync and async facades over an auto-generated
low-level client (`unitysvc._generated`). Callers should prefer
`Client` / `AsyncClient`; the generated layer is an implementation
detail.

## `Client`

```python
from unitysvc import Client

client = Client(
    api_key="svcpass_...",
    base_url=None,         # defaults to $UNITYSVC_API_URL or DEFAULT_API_URL
    api_base_url=None,     # defaults to $UNITYSVC_API_BASE_URL
    s3_base_url=None,      # defaults to $UNITYSVC_S3_BASE_URL
    smtp_base_url=None,    # defaults to $UNITYSVC_SMTP_BASE_URL
    timeout=30.0,
    verify_ssl=True,
)
```

Or from the environment:

```python
client = Client.from_env()  # reads UNITYSVC_API_KEY + UNITYSVC_API_URL
```

`Client` is a context manager:

```python
with Client.from_env() as client:
    client.secrets.list()
```

### Resources

| Namespace             | Backend routes                                              |
|-----------------------|-------------------------------------------------------------|
| `client.secrets`      | `/v1/customer/secrets/*`                                    |
| `client.aliases`      | `/v1/customer/aliases/*`                                    |
| `client.recurrent_requests` | `/v1/customer/recurrent-requests/*`                   |

## `AsyncClient`

```python
import asyncio
from unitysvc import AsyncClient

async def main():
    async with AsyncClient.from_env() as client:
        secrets = await client.secrets.list()
        for s in secrets.data:
            print(s.name)

asyncio.run(main())
```

Every method on `AsyncClient.<resource>.*` is an `async def` with the
same signature as its sync counterpart on `Client`.

## `secrets`

```python
client.secrets.list(skip=0, limit=100)
client.secrets.get(secret_id)
client.secrets.check_exists(name)
client.secrets.create({"name": "openai-key", "value": "sk-..."})
client.secrets.update(secret_id, {"value": "sk-new..."})
client.secrets.delete(secret_id)
```

## `aliases`

```python
client.aliases.list(skip=0, limit=100, name=None, include_deactivated=False)
client.aliases.get(alias_id)
client.aliases.create({...})
client.aliases.update(alias_id, {...})
client.aliases.set_routing(alias_id)
client.aliases.delete(alias_id)
```

!!! note
    The current backend spec has a schema-name collision on
    `RequestRoutingKey` that prevents `openapi-python-client` from
    generating a typed `ServiceAliasPublic` response model. Until the
    backend spec is fixed, alias read methods return loosely-typed
    parsed bodies.

## `recurrent_requests`

```python
client.recurrent_requests.list(
    service_id=None,
    enrollment_id=None,
    status=None,
    skip=0,
    limit=100,
)
client.recurrent_requests.get(request_id)
client.recurrent_requests.create({...})
client.recurrent_requests.update(request_id, {...})
client.recurrent_requests.trigger(request_id)
client.recurrent_requests.delete(request_id)
```

## Errors

All errors are subclasses of `unitysvc.UnitysvcSDKError`:

| Exception             | HTTP status  | Meaning                           |
|-----------------------|--------------|-----------------------------------|
| `AuthenticationError` | 401          | Bad / missing / expired API key   |
| `PermissionError`     | 403          | Authenticated but forbidden       |
| `NotFoundError`       | 404          | Resource does not exist           |
| `ValidationError`     | 400, 422     | Request body rejected by server   |
| `ConflictError`       | 409          | State conflict (e.g. duplicate)   |
| `RateLimitError`      | 429          | Too many requests                 |
| `ServerError`         | 5xx          | Server-side failure               |
| `APIError`            | (base)       | Anything else non-2xx             |

Each carries `status_code`, `detail` (parsed body if JSON), and
`response_body` for debugging.

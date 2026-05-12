# SDK Guide

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

| Namespace                   | Backend routes                          |
|-----------------------------|-----------------------------------------|
| `client.groups`             | `/v1/customer/groups/*`                 |
| `client.services`           | `/v1/customer/services/*`               |
| `client.enrollments`        | `/v1/customer/enrollments/*`            |
| `client.resolve(...)`       | `/v1/customer/resolve` (dry-run)        |
| `client.secrets`            | `/v1/customer/secrets/*`                |
| `client.aliases`            | `/v1/customer/aliases/*`                |
| `client.recurrent_requests` | `/v1/customer/recurrent-requests/*`     |
| `client.request_logs`       | `/v1/customer/request-logs/*`           |

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

## `groups`

Groups are the entry point for service discovery. A group is a
curated set of services (often providers of the same capability —
e.g. "llm", "vision-api") that share a group-level access
interface.

Groups are addressed by **name** (a URL-friendly slug like `"llm"`),
not by UUID — group UUIDs change when admins recreate a group, so
SDK scripts that hardcode a slug survive admin recreations.

`client.groups.get(...)` returns a `Group` object with bound
navigation methods. You can call ops on it directly without
re-passing the slug:

```python
llm = client.groups.get("llm")
page = llm.services(cursor=None, limit=50, search=None)
resp = llm.dispatch(json={"messages": [...]})

# List browse — items in `.data` are also `Group` wrappers.
groups = client.groups.list(name="llm")          # `name` is a substring filter
for grp in groups.data:
    print(grp.name, grp.service_count)
```

Field access on a `Group` is forwarded to the underlying record, so
`grp.name`, `grp.routing_policy`, `grp.interface`, etc. all work
exactly as they do on the raw response model.

## `services`

Services are what you actually dispatch to. Each carries a list of
access interfaces — shared (public) or enrollment-bound
(BYOK/BYOE) — and dispatch or schedule picks among them.

`client.services.get(...)` returns a `Service` object with bound
navigation methods, mirroring the same active-record pattern as
`Group`:

```python
svc = client.services.get(service_id)
ifaces = svc.interfaces()
resp = svc.dispatch(json={"messages": [...]})

# Scheduled dispatch — same interface-resolution rule as .dispatch
svc.schedule(
    recurrence={"schedule_type": "interval", "interval_seconds": 300},
    # or: {"schedule_type": "cron", "cron_expression": "*/5 * * * *"}
    json={...},
    name="health-probe",
)
```

**Interface-resolution rule**: multiple public interfaces all map to
the same upstream, so the SDK auto-picks one — no `interface=`
needed. If the customer has exactly one enrollment-bound interface,
that one wins (BYOK/BYOE keys take precedence over public). When
the customer has 2+ enrollments on the same service, pass
`enrollment=` (or `interface=`) to disambiguate.

Field access on a `Service` is forwarded to the underlying record,
so `svc.id`, `svc.name`, `svc.display_name`, etc. all work as on
the raw response.

## Streaming responses (SSE / NDJSON)

`dispatch()` buffers the full response body before returning, which
defeats streaming UX for LLM SSE and similar protocols. For those,
use the sibling `stream()` methods — same auth and interface
resolution, but the body is consumed lazily.

```python
with client.services.stream(
    svc_id,
    json={"messages": [...], "stream": True},   # upstream-protocol flag
) as r:
    print(r.status_code, r.headers)             # available before iteration
    for event in r.iter_events():
        if event.kind == "done":
            break
        handle(event.parsed)
```

The same surface is available at the group level
(`client.groups.stream(name, ...)`) and on the active-record
wrappers (`svc.stream(...)`, `grp.stream(...)`).

### Two flags to keep distinct

|                                  | Concern         | What it does                                  |
|----------------------------------|-----------------|-----------------------------------------------|
| `json={"stream": True}`          | Upstream        | Tells the provider to emit SSE / NDJSON       |
| Calling `.stream()` vs `.dispatch()` | SDK         | Tells the SDK to iterate, not buffer          |

They're orthogonal — most LLM calls need both. `dispatch()` with the
upstream flag still works (whole SSE body in `r.text`); `stream()`
without the upstream flag still works (you just iterate over a
one-shot non-streaming response).

### Event taxonomy

`iter_events()` discriminates on `Content-Type`:

| `event.kind` | When                                     | `event.parsed`        | `event.raw`           |
|--------------|------------------------------------------|-----------------------|-----------------------|
| `"sse"`      | `text/event-stream`, one per `data:` frame | `dict` (or `str` fallback) | raw frame bytes  |
| `"done"`     | SSE `data: [DONE]` sentinel               | `None`                | `b"[DONE]"`           |
| `"ndjson"`   | `application/x-ndjson` / `application/jsonl`, per line | `dict` | raw line bytes      |
| `"line"`     | any `text/*`, per line                    | `None`                | bytes; `event.text` is the decoded string |
| `"bytes"`    | anything else                             | `None`                | raw chunk bytes       |

SSE frames split across TCP chunks (a frame's bytes arriving in two
`iter_bytes()` deliveries) are reassembled at the parser layer
before they reach you — no buffering on the caller's side is
necessary.

If you need lower-level access, `iter_bytes()` and `iter_lines()`
are also available on the streaming response and pass straight
through to `httpx`.

### Errors and end-of-stream

- Body terminates cleanly → iteration stops naturally.
- SSE `[DONE]` arrives → a final `event.kind == "done"` is yielded,
  then iteration stops (any frames after `[DONE]` are discarded).
- Connection drops mid-stream → `httpx.ReadError` (or similar) is
  raised to the caller from inside `iter_events()`. Retry policy is
  the caller's call.
- HTTP 4xx/5xx with a streaming-shaped body → the context manager
  enters successfully; inspect `r.status_code` and decide whether
  to iterate (this matches `httpx.stream()` behavior).

### Async

```python
async with AsyncClient.from_env() as client:
    async with await client.services.stream(svc_id, json={...}) as r:
        async for event in r.iter_events():
            ...
```

Note the `await` before `client.services.stream(...)` on the async
side — interface resolution is async, so the call that constructs
the streaming response is itself awaitable. The returned object is
then used with `async with`.

### Out of scope

- **WebSocket** dispatch — different protocol; not provided.
- **gRPC** — different framing; use `grpcio` directly.
- **Auto-injection** of the upstream `stream` body flag — the SDK
  doesn't know the upstream's field name (OpenAI uses `stream`,
  others differ); set it yourself.
- **Built-in retry on mid-stream errors** — surfaces the exception
  for the caller to handle.

## `enrollments`

Enrollments record "I've opted into this service with these
parameters (optionally BYOK/BYOE credentials)". For BYOK services,
the parameters include the customer's upstream API key; the
platform mints an enrollment-bound access interface that
substitutes the key at dispatch time.

```python
enr = svc.enroll(parameters={"endpoint": "https://my-host", "api_key": "..."})

# Activation is async. Poll on the wrapper itself:
import time
while enr.status == "pending":
    time.sleep(1)
    enr = enr.refresh()

enr.cancel()                                    # unenroll
```

If you only have an enrollment id (e.g. from a webhook),
`client.enrollments.get(id)` returns the same `Enrollment` wrapper.

Secret-shaped parameter keys (`api_key`, `password`, `token`, ...)
are returned masked (`***masked***`) on reads; only the server has
the raw values.

### Inspecting required secrets

A BYOK/BYOE service won't dispatch until the customer's account has
the secrets the picked interface references (e.g. `OPENAI_API_KEY`).
`Service` exposes those names directly:

```python
svc.required_secrets()                          # list[str]
svc.optional_secrets()                          # list[{"name", "default"}]
svc.required_secrets(interface="raw")           # specific interface
```

Both default to the same interface `dispatch()` would auto-pick, so
in the common case ``svc.required_secrets()`` answers "what do I
need to set up to use this service?". Set the secrets via
``client.secrets.set(name=..., value=...)`` before dispatch /
enrollment.

## `client.resolve(...)` — dry-run routing

Answers "what would the gateway do for this path + routing key?"
without executing the upstream call. Useful for debugging,
simulating selection, or resolving an alias or group path to the
concrete service ahead of dispatch.

```python
res = client.resolve(
    path="v1/chat/completions",
    routing_key={"model": "gpt-4"},
    gateway="api",                # default; also "s3", "smtp"
    strategy=None,                # override group routing_policy if set
)
# res.candidates: list[ResolveCandidate] — service_id/name/provider_name,
#                 weight, enrollment_id per candidate
# res.routing_strategy: {"name", "content_dependent", ...} or None
# res.selected: pre-picked candidate when unambiguous, else None
```

Sensitive fields (`wallet_id`, `customer_secrets`, decrypted
upstream API keys, `seller_id`, `pricing_bundle_id`) are *not*
returned — this is a customer-safe subset of the gateway's
internal route-resolution response.

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

## `request_logs`

Request logging is **opt-in per user**. Until you call
`client.request_logs.start()`, gateway dispatches are not persisted
to the customer-facing log — neither `list()` nor `get()` will see
them. Once started, all subsequent dispatches are recorded until you
call `stop()`. Both toggle calls are idempotent.

```python
# Toggle
client.request_logs.start()  # enable persistence
client.request_logs.stop()   # disable; already-stored rows remain visible
```

```python
# Paginated listing (lightweight columns — no bodies)
page = client.request_logs.list(
    skip=0,
    limit=50,
    service_id=None,             # UUID — filter to one service
    service_enrollment_id=None,  # UUID — filter to one enrollment
    status_min=None,             # int — min upstream status (e.g. 400)
    status_max=None,             # int — max upstream status
    start_time=None,             # datetime — inclusive lower bound
    end_time=None,               # datetime — inclusive upper bound
    user_request_path=None,      # str — path-prefix filter
    error_source=None,           # "gateway" or "upstream"
    error_type=None,             # str — filter by error type
    gateway_source=None,         # "apisix" or "backend"
)
print(page.total_count, len(page.items))

# Full detail of one row (includes request + response bodies, with
# upstream identity / credentials redacted server-side).
detail = client.request_logs.get(page.items[0].log_id)
```

The default time window when both `start_time` and `end_time` are
omitted is the last 24 hours. Use `start_time=datetime.now(UTC) - timedelta(hours=1)`
to narrow further; combined with a `service_id` filter this is the
fastest way to verify that a specific dispatch was recorded.

### Common patterns

**Verify a dispatch was logged**

```python
import datetime as dt

t0 = dt.datetime.now(dt.timezone.utc)
client.request_logs.start()
client.services.dispatch(svc_id, json={"messages": [...]})

# Brief settle window (Kafka → ClickHouse pipeline is async)
import time; time.sleep(2)

page = client.request_logs.list(service_id=svc_id, start_time=t0)
assert page.total_count >= 1
```

**Inspect a 5xx**

```python
errs = client.request_logs.list(
    status_min=500,
    status_max=599,
    error_source="upstream",
)
for row in errs.items:
    detail = client.request_logs.get(row.log_id)
    print(detail.upstream_response.status_code, detail.error)
```

**Async**

```python
async with AsyncClient.from_env() as client:
    await client.request_logs.start()
    await client.services.dispatch(svc_id, json={"messages": [...]})
    page = await client.request_logs.list(service_id=svc_id, limit=10)
```

### Notes

- **Auth.** Both API key and JWT (frontend session) reach the same
  routes. The SDK uses your API key.
- **Idempotency.** `start()` and `stop()` are safe to call repeatedly;
  the route reconciles state and returns the post-call value.
- **Privacy.** `get(log_id)` returns server-side-redacted bodies —
  upstream-identifying response headers and credentials are stripped
  before the response leaves the backend (see
  [unitysvc#881](https://github.com/unitysvc/unitysvc/pull/881)).

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

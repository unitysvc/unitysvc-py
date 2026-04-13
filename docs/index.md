# UnitySVC Customer SDK

`unitysvc-py` is the customer-facing Python SDK and `usvc` CLI for
[UnitySVC](https://unitysvc.com/).

It wraps the customer-tagged backend API with a typed sync
([`Client`](sdk-reference.md#client)) and async
([`AsyncClient`](sdk-reference.md#asyncclient)) surface, plus a
[`usvc`](cli-reference.md) command-line tool for day-to-day operations.

!!! note "Early scaffolding"
    The customer API currently exposes a small set of endpoints
    (aliases, recurrent requests, secrets). The SDK tracks those today
    and will grow as the backend adds more.

## Quick links

- [Getting Started](getting-started.md) — install, configure, first request
- [CLI Reference](cli-reference.md) — every `usvc` subcommand
- [SDK Reference](sdk-reference.md) — every resource and method

## At a glance

```python
from unitysvc import Client

client = Client.from_env()  # reads UNITYSVC_API_KEY + UNITYSVC_API_URL
secrets = client.secrets.list()
for s in secrets.data:
    print(s.name)
```

```bash
usvc secrets list
usvc secrets set openai-key --value sk-...
usvc aliases list
usvc recurrent-requests list
```

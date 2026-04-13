# Getting Started

## Install

```bash
pip install unitysvc-py
```

This pulls in `httpx`, `attrs`, `typer`, and `rich` — everything the
SDK and CLI need.

## Configure

All configuration comes from environment variables. Only
`UNITYSVC_API_KEY` is required.

| Variable                 | Purpose                                     | Default                                      |
|--------------------------|---------------------------------------------|----------------------------------------------|
| `UNITYSVC_API_KEY`       | Customer API key (`svcpass_...`)            | (required)                                   |
| `UNITYSVC_API_URL`       | Control-plane API base URL                  | `https://api.unitysvc.com/v1`   |
| `UNITYSVC_API_BASE_URL`  | HTTP API gateway base URL (inference)       | (unset)                                      |
| `UNITYSVC_S3_BASE_URL`   | S3-compatible gateway base URL              | (unset)                                      |
| `UNITYSVC_SMTP_BASE_URL` | SMTP gateway base URL                       | (unset)                                      |

Typical shell setup:

```bash
export UNITYSVC_API_KEY="svcpass_..."
export UNITYSVC_API_URL="https://customer.unitysvc.com/v1"
```

The customer context is encoded entirely in the API key — no separate
`customer_id` argument is required.

`UNITYSVC_API_URL` is what the SDK and CLI use for control-plane calls
(listing and managing secrets, aliases, recurrent requests). The
`*_BASE_URL` variables are exposed on `Client` as properties
(`client.api_base_url`, `client.s3_base_url`, `client.smtp_base_url`)
for downstream inference / storage / email SDKs to pick up. The
customer SDK itself never talks to them directly.

## First SDK call

```python
from unitysvc import Client

with Client.from_env() as client:
    secrets = client.secrets.list()
    for s in secrets.data:
        print(s.name)
```

## First CLI call

```bash
# Check that env vars resolve correctly
usvc env

# List the authenticated customer's secrets
usvc secrets list

# Upsert a secret by name
usvc secrets set openai-key --value sk-xxx

# Or from a file
usvc secrets set openai-key --from-file ~/.secrets/openai
```

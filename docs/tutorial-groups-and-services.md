# Tutorial: Browse groups, dispatch services, enroll for BYOK

This tutorial walks through the customer SDK's four main verbs:

1. **Browse** a service group and its member services
2. **Dispatch** a one-shot request through a service's interface
3. **Enroll** in a service with your own upstream credentials (BYOK)
4. **Schedule** a recurring dispatch

We'll use a hypothetical `llm` group throughout. Adjust names to
match what's actually configured on your account.

---

## Setup

```python
import os
from unitysvc import Client

client = Client(api_key=os.environ["UNITYSVC_API_KEY"])
# or: client = Client.from_env()
```

The API key encodes your customer identity — no separate
`customer_id` is required anywhere in the SDK.

---

## 1. Browse a group

Groups are the discovery entry point. Find one by its platform-unique
name, then list its member services.

```python
llm = client.groups.get_by_name("llm")
print(llm.name, llm.display_name)
print("services:", llm.service_count)

# Drill into members:
members = client.groups.services(llm.id)
for svc in members.data:
    print(f"  {svc.name}  ({svc.provider_name})")
```

`client.groups.services(group_id)` is the **canonical**
service-discovery path — there's intentionally no flat
`client.services.list()`, because services are only meaningful
within the context of a group.

Need more than just names? Narrow the result with `search=`:

```python
chat_services = client.groups.services(llm.id, search="chat")
```

---

## 2. Dispatch a one-shot request

Pick a member service, look at its interfaces, and call it.

```python
svc = members.data[0]
ifaces = client.services.interfaces(svc.id)
for i in ifaces:
    print(f"  {i.name}  base_url={i.base_url}  enrollment={i.enrollment_id}")

response = client.services.dispatch(
    svc.id,
    # interface="chat" needed only when the service has >1 interface
    json={"messages": [{"role": "user", "content": "hello"}]},
)
print(response.status_code, response.json())
```

### Interface-resolution rule

- **Exactly one interface** → used automatically, `interface=` is
  ignored.
- **More than one** → `interface=` is *required* (by name or UUID).
  Interfaces are typically different **operations** (chat vs
  embeddings, put vs list), not alternatives, so the SDK refuses to
  guess.
- **`enrollment=` hint** → picks the interface whose
  `enrollment_id` matches. Useful after BYOK enrollment
  (see step 3).

### Group-level dispatch

If the group itself has an access interface (a single entry on
`group.interface`), you can dispatch *without* picking a specific
service — the gateway applies the group's `routing_policy` to
select a member on each call (weighted random, by price, by
latency, by content, ...).

```python
resp = client.groups.dispatch(
    llm.id,
    json={"messages": [{"role": "user", "content": "hello"}]},
)
```

This is the recommended path for multi-provider groups where
customers don't want to pick a specific service themselves.

### Dry-run with `resolve()`

Before dispatch, you can ask the gateway **which service it would
pick** without making the upstream call:

```python
plan = client.resolve(
    path="v1/chat/completions",
    routing_key={"model": "gpt-4"},
)
for c in plan.candidates:
    print(f"  {c.service_name} @ weight={c.weight}")
if plan.selected:
    print(f"→ would pick: {plan.selected.service_name}")
```

Same candidate identity the real dispatch uses, minus the actual
HTTP call and sensitive fields (`wallet_id`, upstream API keys,
and so on).

---

## 3. Enroll with BYOK / BYOE

"Bring Your Own Key" services require per-customer credentials.
Enrolling creates a customer-bound access interface that the
gateway uses to substitute your key at dispatch time.

```python
# Enroll — activation is async; server validates parameters and
# mints the access interface in the background.
enr = client.enrollments.create(
    service_id=svc.id,
    parameters={
        "endpoint": "https://my-host.example",
        "api_key": "sk-my-provider-key",
    },
)
print("enrolled:", enr.id, enr.status)   # "pending" initially

# Poll for activation (a few seconds):
import time
for _ in range(15):
    cur = client.enrollments.get(enr.id)
    if cur.status != "pending":
        break
    time.sleep(1)
print("now:", cur.status)  # "active", "incomplete", or "pending"

# Dispatch using your enrollment:
resp = client.services.dispatch(
    svc.id,
    enrollment=enr.id,            # → picks enrollment-bound interface
    json={"messages": [...]},
)
```

Parameters that look like secrets (`api_key`, `password`, `token`,
`secret_key`, ...) are returned **masked** on reads — the server
keeps the raw values.

To stop using an enrollment:

```python
client.enrollments.cancel(enr.id)
# The interface is preserved so re-enrolling with the same
# parameters reactivates it.
```

---

## 4. Schedule a recurring dispatch

`service.schedule()` is `service.dispatch()` + a recurrence spec.
Same interface-resolution rule; instead of making the call now, the
server runs it on your schedule.

```python
# Every 5 minutes:
sched = client.services.schedule(
    svc.id,
    recurrence={"schedule_type": "interval", "interval_seconds": 300},
    json={"messages": [{"role": "user", "content": "ping"}]},
    name="chat-ping",
)
print("scheduled:", sched.id, sched.status)  # "active"

# Cron (if your service allows it):
sched = client.services.schedule(
    svc.id,
    recurrence={
        "schedule_type": "cron",
        "cron_expression": "0 */6 * * *",
        "timezone": "UTC",
    },
    json={"prompt": "daily summary"},
    name="summary-job",
)

# Inspect / manage via the recurrent_requests namespace:
all_scheduled = client.recurrent_requests.list()
client.recurrent_requests.trigger(sched.id)      # fire once on demand
client.recurrent_requests.delete(sched.id)       # stop and remove
```

Scheduled requests inherit the same auth (your API key) and
interface resolution as one-shot dispatch. Per-service limits on
minimum / maximum interval and cron usage are enforced server-side.

---

## Putting it together

```python
from unitysvc import Client

with Client.from_env() as client:
    llm = client.groups.get_by_name("llm")

    # Option A — group-level, let the gateway pick:
    resp = client.groups.dispatch(
        llm.id,
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    print(resp.json())

    # Option B — specific service + specific interface:
    members = client.groups.services(llm.id)
    gpt4 = next(s for s in members.data if s.name == "gpt-4")
    resp = client.services.dispatch(
        gpt4.id,
        interface="chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    print(resp.json())
```

---

## Further reading

- [SDK Guide](sdk-guide.md) — full resource reference
- [SDK Reference](sdk-reference.md) — auto-generated from docstrings
- [CLI Reference](cli-reference.md) — `usvc` commands

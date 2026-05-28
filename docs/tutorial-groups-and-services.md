# Tutorial: Browse groups, dispatch services, enroll, build collections

This tutorial walks through the customer SDK's main verbs:

1. **Browse** a service group and its member services
2. **Dispatch** a one-shot request through a service's interface
3. **Enroll** in a service with your own upstream credentials (BYOK)
4. **Schedule** a recurring dispatch
5. **Create** your own collection — a customer-curated group of
   subscribed services, addressable at `/g/<name>`

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

Groups are the discovery entry point. They're identified by a
**slug name** (e.g. `"llm"`, `"vision-api"`) — names are stable
across admin-side recreations, while group UUIDs aren't, so SDK
scripts should hardcode the slug rather than the UUID.

`client.groups.get(...)` returns a `Group` object with bound
navigation methods, so you can chain calls without re-passing the
slug:

```python
llm = client.groups.get("llm")
print(llm.name, llm.display_name)
print("services:", llm.service_count)

# Drill into members (cursor-paginated). Items are `Service`
# wrappers ready for further navigation.
page = llm.services()
for svc in page.data:
    print(f"  {svc.name}  ({svc.provider_name})")

# Next page:
if page.has_more:
    page = llm.services(cursor=page.next_cursor)
```

`grp.services()` is the **canonical** service-discovery path —
there's intentionally no flat `client.services.list()`, because
services are only meaningful within the context of a group.

Need more than just names? Narrow the result with `search=`:

```python
chat_services = llm.services(search="chat")
```

---

## 2. Dispatch a one-shot request

Pick a member service, look at its interfaces, and call it. Items
in `page.data` are already `Service` wrappers, so you can chain
calls directly:

```python
svc = page.data[0]                                # already a Service wrapper
ifaces = svc.interfaces()
for i in ifaces:
    print(f"  {i.name}  base_url={i.base_url}  enrollment={i.enrollment_id}")

response = svc.dispatch(
    json={"messages": [{"role": "user", "content": "hello"}]},
)
print(response.status_code, response.json())
```

If you only have a service id (e.g. from a webhook payload),
fetch a wrapper first: `svc = client.services.get(service_id)`.

### Interface-resolution rule

- **Multiple public interfaces** all map to the same upstream — the
  SDK auto-picks one. No `interface=` required in the common case.
- **One enrollment-bound interface** (e.g. after BYOK) → preferred
  over public interfaces; the customer enrolled to use their own
  key/parameters.
- **`interface=`** is only required to disambiguate when the customer
  has 2+ enrollments on the same service. **`enrollment=`** is an
  equivalent hint that picks by `enrollment_id`.

### Group-level dispatch

If the group itself has an access interface (a single entry on
`group.interface`), you can dispatch *without* picking a specific
service — the gateway applies the group's `routing_policy` to
select a member on each call (weighted random, by price, by
latency, by content, ...).

```python
resp = llm.dispatch(json={"messages": [{"role": "user", "content": "hello"}]})
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

Before enrolling, check what the service needs:

```python
print("required:", svc.required_secrets())   # e.g. ["MY_PROVIDER_API_KEY"]
print("optional:", svc.optional_secrets())   # list of {"name", "default"}
```

Set the required secrets on your account, then enroll:

```python
client.secrets.set(name="MY_PROVIDER_API_KEY", value="sk-...")

# Active-record enrollment — pre-binds the service id.
enr = svc.enroll(parameters={
    "endpoint": "https://my-host.example",
})
print("enrolled:", enr.id, enr.status)   # "pending" initially

# Poll for activation (a few seconds):
import time
while enr.status == "pending":
    time.sleep(1)
    enr = enr.refresh()
print("now:", enr.status)  # "active", "incomplete", or "pending"

# Dispatch — picks the enrollment-bound interface automatically.
resp = svc.dispatch(json={"messages": [...]})
```

Parameters that look like secrets (`api_key`, `password`, `token`,
`secret_key`, ...) are returned **masked** on reads — the server
keeps the raw values.

To stop using an enrollment:

```python
enr.cancel()
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
sched = svc.schedule(
    recurrence={"schedule_type": "interval", "interval_seconds": 300},
    json={"messages": [{"role": "user", "content": "ping"}]},
    name="chat-ping",
)
print("scheduled:", sched.id, sched.status)  # "active"

# Cron (if your service allows it):
sched = svc.schedule(
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

## 5. Create and manage your own collection

The groups you browse in section 1 are **platform** groups —
admin-curated, read-only. You can also create your **own** groups,
called *collections*: editable, customer-curated catalogs of services
you're subscribed to, addressable at `/g/<your-collection-name>` just
like a platform group. The common use case is pointing a third-party
tool (LiteLLM, LangChain, an IDE plugin) at a single base URL whose
`/models` endpoint returns exactly the set you picked.

Both kinds show up in `client.groups.list()`. Each row carries an
`owner_type` (`"platform"` or `"customer"`) and an `editable` flag, so
you can tell yours apart and filter with `owner=`:

```python
# Everything you can see (default):
client.groups.list()                 # owner="all"
# Just the platform catalogue:
client.groups.list(owner="system")
# Just your own editable collections:
mine = client.groups.list(owner="own")
for row in mine.data:
    print(row.name, row.owner_type, row.editable, row.member_count)
```

### Create a collection and add members

`create` returns the new collection as a `Group`. Members must be
services you're subscribed to (you have an active enrollment) — adding
an unsubscribed service is rejected. A collection holds up to 20
members.

```python
coll = client.groups.create(
    name="my-llms",                  # the /g/<name> slug; lowercase, [a-z0-9_-]
    display_name="My LLMs",
)

# Add a subscribed service. The optional routing_key OVERRIDES the
# service's native model id so you can expose uniform names across
# providers — here OpenAI's gpt-4o is surfaced to your apps as
# "fast-gpt".
client.groups.add_member(
    coll.id,
    service_id=openai_gpt4o_service_id,
    routing_key={"model": "fast-gpt"},
)
# Omit routing_key to keep the service's native model id.
client.groups.add_member(coll.id, service_id=claude_service_id)

# Inspect membership:
for m in client.groups.members(coll.id):
    print(m.service_id, m.routing_key)
```

Management methods are **UUID-keyed** — pass the collection's `id`
(`coll.id`), not its slug. (The slug is reserved for the `/g/<name>`
dispatch path.)

### Dispatch against your collection

Hitting `/g/my-llms` routes to a member by matching the request's
`model` field against each member's effective routing key (your
override, or the service's native id):

```python
mine = client.groups.get(coll.id)     # resolvable by id or name

# Routes to the member whose routing key is {"model": "fast-gpt"}:
resp = mine.dispatch(json={"model": "fast-gpt", "messages": [...]})

# No `model` field → the gateway picks across all members
# (weighted by each service's access-interface weights).
resp = mine.dispatch(json={"messages": [...]})
```

If two members share the same `model` routing key, the gateway
load-balances across them. An unknown `model` returns a 404 listing
the collection's available ids. The collection's `/models` endpoint
returns the deduplicated set of those ids, so an OpenAI-compatible
client pointed at the collection sees exactly your curated names.

### Update / remove

```python
client.groups.update(coll.id, display_name="My Production LLMs")
client.groups.remove_member(coll.id, service_id=claude_service_id)
client.groups.delete(coll.id)
```

Only your own collections are editable — `update` / `delete` /
member changes on a platform group return 403.

---

## Putting it together

```python
from unitysvc import Client

with Client.from_env() as client:
    llm = client.groups.get("llm")

    # Option A — group-level, let the gateway pick:
    resp = llm.dispatch(
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    print(resp.json())

    # Option B — specific service + specific interface:
    members = llm.services()
    gpt4 = next(s for s in members.data if s.name == "gpt-4")
    resp = gpt4.dispatch(
        interface="chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    print(resp.json())
```

---

## Same flow from the CLI

Every step above has a `usvc` counterpart — handy for shell pipelines or
quick one-offs without writing Python:

```bash
# 1. Browse a group + its services
usvc groups list
usvc groups services llm

# 2. One-shot dispatch (body to stdout, status to stderr)
usvc services dispatch <service-id> \
    --json '{"messages": [{"role": "user", "content": "Hello"}]}'

# 3. BYOK enrollment
usvc services enroll <service-id> \
    --parameter api_key=sk-... \
    --parameter endpoint=https://my-host

usvc enrollments list
usvc enrollments cancel <enrollment-id>

# 4. Schedule a recurring dispatch — --interval / --cron sugar over the
#    full --recurrence JSON form
usvc services schedule <service-id> \
    --interval 300 \
    --json '{"prompt": "ping"}' \
    --name "5-min ping"

# Dry-run a route to inspect candidates without sending the upstream call
usvc resolve --path v1/chat/completions --routing-key '{"model": "gpt-4"}'
```

See [CLI Reference](cli-reference.md) for the full option list.

---

## Further reading

- [SDK Guide](sdk-guide.md) — full resource reference
- [SDK Reference](sdk-reference.md) — auto-generated from docstrings
- [CLI Reference](cli-reference.md) — `usvc` commands

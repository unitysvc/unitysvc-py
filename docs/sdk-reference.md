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

After an enrollment activates, its `resources` list identifies provisioned
rooms by `object` (the Python attribute is `object_`), `kind` and `room_id`.
Read the enrollment again after the
initial create acknowledgement to discover these resources:

```python
enrollment = client.enrollments.get(enrollment_id)
if isinstance(enrollment.resources, list):
    for resource in enrollment.resources:
        if resource.object_ == "resource:room":
            room = client.rooms.get(str(resource.room_id))
```

::: unitysvc.enrollments.Enrollments
    options:
      show_root_heading: true

### Files

Account files follow the API key's customer. Legacy `scope="personal"` paths
map to `home/`; use `scope=None` for the full account tree, and a team key for
team files. The removed shared-scope selector is refused rather than silently
selecting another account.

::: unitysvc.files.Files
    options:
      show_root_heading: true

### Rooms

```python
room = client.rooms.get("helpdesk")
client.rooms.post("helpdesk", body="Please help", client_message_id="support-1")
client.rooms.update(str(room.id), description="Contact **our support team** here.")
members = client.rooms.members(str(room.id))
delivery = client.rooms.delivery(str(room.id))
if delivery.can_edit:
    client.rooms.set_delivery(str(room.id), notify="auto", email="off")
# Owner only: pause the room with an automatic reply, then resume it.
client.rooms.update(str(room.id), status="paused", pause_message="Back on Monday.")
client.rooms.update(str(room.id), status="active", pause_message=None)
```

Descriptions are owner-written Markdown. Policy fields such as `retention_seconds`,
`max_retention_seconds`, `owner_sets_retention` and `keep_forever` describe the
rules actually enforced by the server. A null maximum means the kind has no
retention cap. Owners can change retention only when `owner_sets_retention` is
true.

`role` is the role you act with now. It comes from your admissions that are
still live: an admission through an enrollment counts only while that
enrollment is active. A room you can no longer reach is not listed, and
reading it returns 404. `status` is the owner's operational setting:
`active`; `paused`, where messages are still accepted and each sender gets the
owner's `pause_message` once, privately; or `readonly`, where only the owner
and moderators post. `status_changed_at` says when it last changed.

::: unitysvc.rooms.Rooms
    options:
      show_root_heading: true

::: unitysvc.arooms.AsyncRooms
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

### Preferences

::: unitysvc.preferences.Preferences
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

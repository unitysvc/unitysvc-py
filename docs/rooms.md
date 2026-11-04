# Rooms

A **room** is a message space on UnitySVC: your private notes, your
conversation with UnitySVC support, or a group chat that came with an
enrollment. This guide covers what rooms are and every operation the SDK and
the `usvc rooms` CLI offer. For the full method signatures, see the
[SDK Reference](sdk-reference.md#rooms).

## Kinds of rooms

| Kind | What it is | Members | Messages kept |
|---|---|---|---|
| `me` | Your account's private room for notes and saved messages. Webhook posts that name no room land here, so none is lost. | Only your account | Up to 30 days |
| `helpdesk` | Your account's conversation with UnitySVC support. | Your account and UnitySVC support | Forever |
| `chat` | A group room. An enrollment can provide one (for example a community service), and its owner invites others with a code. | The owner and the people they invite | Up to 7 days; the owner may keep less, or nothing |

Every account has one `me` and one `helpdesk` room, created on first use.
Each room you're in has a **handle**: `me`, `helpdesk`, or a short name such
as `book-club`. Anywhere a room is expected, you can pass its id or your
handle for it.

More kinds are planned: seller-run `support` rooms (one per enrollment) and
service-wide `announcement` / `discussion` rooms
([unitysvc#2830](https://github.com/unitysvc/unitysvc/issues/2830)).

## Your role decides what you can do

Each room you're in lists your `role`:

| Role | Read | Post | Invite | Change settings |
|---|---|---|---|---|
| `owner` | ✓ | ✓ | up to `moderator` | ✓ |
| `moderator` | ✓ | ✓ | up to `member` | |
| `member` | ✓ | ✓ | | |
| `readonly` | ✓ | | | |

Your role is the one you hold **now**. It comes from how you were admitted:
directly, by an invitation code, or through an enrollment. An admission
through an enrollment counts only while that enrollment is active. Pausing or
cancelling the enrollment closes its rooms without deleting anything, and
reactivating it opens them again. A room you can't reach isn't listed, and
reading it returns 404.

The owner can also set the room's `status` to `readonly`, so that only the
owner and moderators post, and back to `active`.

## List your rooms

```python
from unitysvc import Client

client = Client()  # reads UNITYSVC_API_KEY

for room in client.rooms.list().data:
    print(room.handle, room.kind, room.role)

chats = client.rooms.list(kind="chat")
for_one_enrollment = client.rooms.list(enrollment=enrollment_id)
acme = client.rooms.list(q="acme")                # name starts with "acme", any case
waiting = client.rooms.list(new_activity=True)    # activity you haven't seen
```

Each row also says whether this key can post there (`can_post`) and who sent
the latest message (`last_sender_name`, or `sent_latest_message` when it was
you). Without `limit` the list holds every room; with it, read the next page
with `cursor=page.next_cursor` until `next_cursor` is null:

```python
page = client.rooms.list(limit=50)
while True:
    for room in page.data:
        print(room.name, room.last_sender_name, room.can_post)
    if page.next_cursor is None:
        break
    page = client.rooms.list(limit=50, cursor=page.next_cursor)
```

A service can ask, when you enroll, to create a room for you: its channel
lists a `resource:room` request. Approve it by passing the request back in
`policy`; the platform creates the room when the enrollment activates:

```python
enrollment = client.enrollments.create(
    service_id=service_id,
    policy=[{"object": "resource:room", "permissions": ["create"], "options": "kind=chat&max_members=20"}],
)
```

An enrollment lists its own rooms:

```python
enrollment = client.enrollments.get(enrollment_id)
for room in enrollment.rooms().data:
    print(room.name)
```

```bash
usvc rooms list
usvc rooms list --kind chat
usvc rooms list --enrollment <enrollment-id>
```

## Read a room

`get` returns the room and a page of its messages, oldest first. To read on,
pass the page's `next` as `after`:

```python
page = client.rooms.get("helpdesk")
for message in page.messages.data:
    print(message.offset, message.sender_name, message.body)

more = client.rooms.get("helpdesk", after=page.messages.next_, limit=100)

latest = client.rooms.get("helpdesk", tail=20)  # the newest 20, oldest first
newer = client.rooms.get("helpdesk", after=latest.messages.next_)  # only what came after
```

```bash
usvc rooms show helpdesk
usvc rooms show helpdesk --after 41 --limit 100
```

A message you just posted can take a moment to appear in history: a room is
read only up to what has been fully stored, so a page never skips a message.

## Post

```python
client.rooms.post("helpdesk", body="My invoice shows two charges.")
client.rooms.post(
    "book-club",
    body="Chapter 3 tonight",
    title="Reminder",
    client_message_id="reminder-2026-10-31",
)
```

```bash
usvc rooms post helpdesk "My invoice shows two charges."
usvc rooms post book-club "Chapter 3 tonight" --title Reminder --id reminder-2026-10-31
```

### Files and pictures

Attach files by path (stored for 7 days, then shown as expired) or `http(s)`
URLs (kept as links). A message can be files alone:

```python
client.rooms.post("helpdesk", body="The export fails like this:", attachments=["~/Desktop/error.png"])
client.rooms.post("helpdesk", attachments=["report.pdf", "https://example.com/spec.pdf"])

from unitysvc import attachments
client.rooms.post("helpdesk", attachments=[attachments.from_bytes(png_bytes, "chart.png")])
```

```bash
usvc rooms post helpdesk "The export fails like this:" --attach ~/Desktop/error.png
usvc rooms post helpdesk --attach report.pdf --attach notes.txt
```

A message carries at most 10 files, 10 MiB each and 25 MiB in all; these are
checked before anything is uploaded. The platform checks each file's type from
its bytes and accepts images, PDF, text, CSV and office documents (an HTML or
SVG file is kept as plain text, never displayed as a page).

A received attachment has `filename`, `mime_type`, `size`, a short-lived signed
`url`, and `expired` once the 7 days are over. `attachments.save(attachment,
directory)` downloads one under a cleaned name, without sending your
credentials, never overwriting a file and never opening it: another member
chose its name and bytes.

A post to a room you can't post in goes to your `me` room instead (the
response's `routed` says `me`). Pass `fallback=False` to get an error instead,
as an interactive client should.

`client_message_id` makes a post safe to retry: the same key posts the
message once, for 24 hours. Use it whenever a script or an agent might send
the same message twice.

## Chat in the terminal

`usvc rooms chat` opens a room and keeps it live: new messages appear as they
are stored, and what you type is posted to that room. It needs prompt_toolkit
(`pip install "unitysvc-py[chat]"`, which also brings Pillow for pasting images)
and a key with `api:rooms` read and write. On Linux, pasting images uses
`wl-paste` or `xclip`; over SSH, use `/attach` instead (the clipboard is the
remote machine's).

```bash
usvc rooms chat                       # the most recently active room
usvc rooms chat @helpdesk             # by handle, id or name prefix
usvc rooms chat --enrollment <id>     # the room an app made for an enrollment
usvc rooms chat --join <CODE>         # redeem an invitation, then open the room
```

Inside the chat, Enter posts (Esc then Enter adds a line) and these commands work:

| Command | |
|---|---|
| `/rooms` | list rooms: `●` new activity, `⚑` flagged to follow up, the latest sender, `(read-only)` where you can't post |
| `/open ROOM` | switch: a number from `/rooms`, `@handle`, id or name prefix |
| `/next`, Ctrl-N | open the next room with new activity |
| `/members` | who is in the room |
| `/follow [off]` | flag the room to revisit, or clear the flag |
| `/older`, `/more` | show the messages before the earliest one shown |
| `/attach PATH`, Ctrl-V | attach a file to your next message; Ctrl-V attaches a copied image, or files copied in Finder or Explorer |
| `/drop` | remove the attached files |
| `/save N [DIR]` | download attachment N (they are numbered as shown) into DIR, the current directory by default |
| `/refresh`, `/help`, `/quit` (Ctrl-D) | |

New messages arrive through one long-polled feed for all your rooms
(`rooms.feed`, below), so the chat sees activity in every room without
polling each one, and the bottom bar counts the other rooms waiting for you.
A room opens at its latest messages (`rooms.get(room, tail=50)`), so a long
history isn't read from the start; `/older` reads the page before them
(`rooms.get(room, tail=50, before=messages.previous)`) until `previous` is
null. The chat records what you have seen the way
the web inbox does: when a room opens and when you switch away or quit, never
just because a new message arrived while it was open. It only ever posts to
the open room (`rooms.post(room, ..., fallback=False)`): if the room can't take
the post, the chat says so and nothing is posted anywhere else. Sellers use the same chat
as `usvc_seller rooms chat`, and programs can reuse it through
`unitysvc.chat.ChatSession`.

The same SDK methods are available directly:

```python
client.rooms.unread()                     # rooms with activity you haven't seen
client.rooms.mark_active("helpdesk", 42)  # you've seen it through offset 42
client.rooms.set_follow_up("helpdesk")    # flag it; set_follow_up(..., False) clears
```

## Follow new messages in every room

`rooms.feed` returns new messages from all your rooms, each tagged with its
`room_id`. The first call (no `since`) only takes the current position: it
returns no backlog. Pass its `cursor` back as `since` to get what was stored
after it; `wait` (up to 25 seconds) holds the request until something arrives,
so a loop of feed calls is a live stream over plain HTTP:

```python
feed = client.rooms.feed()                 # start here, no backlog
while True:
    feed = client.rooms.feed(since=feed.cursor, wait=20)
    for message in feed.messages:
        print(message.room_id, message.sender_name, message.body)
```

Keep `wait` below the client's timeout (30 seconds by default). `rooms=[...]`
narrows the feed to some rooms. If a saved cursor is rejected
(`ValidationError`), start again with a call without `since`. Reading the feed
records nothing as seen; call `mark_active` when a person has actually seen a
room.

## Members

```python
for member in client.rooms.members("book-club").data:
    print(member.name, member.role)
```

```bash
usvc rooms members book-club
```

## Room settings (owner)

```python
client.rooms.update(room_id, name="Book club", description="We read **one book a month**.")
client.rooms.update(room_id, retention_seconds=24 * 3600)  # keep messages a day
client.rooms.update(room_id, status="readonly")            # only owner and moderators post
```

```bash
usvc rooms set book-club --description "We read one book a month."
usvc rooms set book-club --retention 86400 --status readonly
```

Descriptions are Markdown. `retention_seconds` can't exceed the kind's
maximum (`max_retention_seconds` on the room), and `0` stores nothing. The
`me` and `helpdesk` rooms keep their fixed retention.

## Invitations, joining and leaving

Owners and moderators invite with a code; anyone with the code joins:

```python
code = client.rooms.create_invitation("book-club", role="member", max_uses=10, expires_in_days=7)
print(code.token)  # share this

client.rooms.join("ABCD1234")         # as the invited account
client.rooms.leave("book-club")       # leave again
```

```bash
usvc rooms invite book-club --role member --max-uses 10
usvc rooms invitations book-club --all
usvc rooms revoke book-club <code-id>
usvc rooms join ABCD1234
usvc rooms leave book-club
```

Only `chat` rooms take invitations, and only their members (never the owner)
can leave. Leaving ends the admissions you made yourself; a membership that
comes from an enrollment follows the enrollment instead.

## How a room reaches you

Each room has delivery settings for you: `notify` (a notification service,
for example `labs/msg-to-discord`) and `email`. Each is `auto` (your
account's default), `off`, or a service path.

```python
settings = client.rooms.delivery("book-club")
client.rooms.set_delivery("book-club", notify="auto", email="off")
```

```bash
usvc rooms delivery book-club
usvc rooms delivery book-club --notify labs/msg-to-discord
```

New messages always show up in the web app's notifications. Delivery through
your notify and email services is planned
([unitysvc#2807](https://github.com/unitysvc/unitysvc/issues/2807) Phase 3):
the settings are stored now and apply once it ships.

## Posting from other systems

A key with the `api:rooms` grant can post without the SDK, through the room
webhook on the UnitySVC web app:

```
POST https://unitysvc.com/rooms/<API_KEY>/<room id or handle>
{"body": "Build 482 passed"}
```

Without a room in the path, a leading `@handle` in the body picks the room,
and a post that matches no room lands in `me`. A key can be limited to some
rooms with the `room=` option on its `api:rooms` grant. The key is part of
the URL, so prefer the SDK, which sends it in a header, where you can.

## Support joining a room

UnitySVC support can join a room to help, for example when you report a
problem in a chat room. When it joins or leaves, the room gets a visible
system message, so its members always know.

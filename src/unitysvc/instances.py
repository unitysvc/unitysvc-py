"""``client.instance(enrollment_id)`` — the container instance an enrollment runs as.

A container service has no gateway route: you start its instance, wait for it
to come up, call its entries, and stop it (unitysvc/unitysvc#3016). The
instance has the same id as its enrollment and exists once started, so an
:class:`Instance` is a cheap handle: build it freely, nothing is fetched until
you call a method::

    instance = client.instance(enrollment_id)
    instance.start()
    state = instance.wait(timeout=300)     # "succeeded" or "failed"
    if state.status == "succeeded":
        key = instance.credentials().key
        print(state.entries[0].url)
    instance.stop()

Needs an API key with the ``api:*`` scope."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from uuid import UUID

from ._http import LowLevelClient, unwrap
from .exceptions import InstanceSuperseded

if TYPE_CHECKING:
    from ._generated.models.enrollment_instance import EnrollmentInstance
    from ._generated.models.enrollment_instance_credentials import EnrollmentInstanceCredentials
    from .client import Client

# Statuses at which a start or stop request has finished.
INSTANCE_FINISHED = ("succeeded", "failed")

# Headroom between a long poll and the HTTP read timeout, so the server's answer to a poll that
# runs to its end arrives before the client gives up on it.
_POLL_MARGIN = 5.0


def _poll_seconds(client: LowLevelClient, remaining: float) -> int:
    """How long one long poll may hold: the time left, at most 60 s (the server's limit), and short
    enough to finish inside the client's own read timeout (30 s by default)."""
    limit = 60.0
    timeout = getattr(client, "_timeout", None)
    read = getattr(timeout, "read", None)
    if read is not None:
        limit = min(limit, read - _POLL_MARGIN)
    return int(max(1, min(limit, remaining)))


class Instance:
    """The instance of one enrollment: ``start`` / ``stop`` / ``get`` / ``wait`` / ``credentials``."""

    def __init__(self, client: LowLevelClient, enrollment_id: str | UUID, *, parent: Client | None = None) -> None:
        self._client = client
        self._parent = parent
        self.enrollment_id = enrollment_id if isinstance(enrollment_id, UUID) else UUID(str(enrollment_id))

    def __repr__(self) -> str:
        return f"Instance(enrollment_id={self.enrollment_id})"

    def get(self, *, wait: int = 0) -> EnrollmentInstance:
        """The request, its status and the pods.

        ``wait`` (0-60 seconds) holds the answer until the current request has
        finished (``succeeded`` or ``failed``) or the time is up. Raises
        :class:`~unitysvc.exceptions.NotFoundError` while nothing has been
        started. A ``failed`` instance names whose problem it is in ``fault``
        (``"platform"`` or ``"seller"``).
        """
        from ._generated.api.customer import get_enrollment_instance

        return unwrap(get_enrollment_instance.sync_detailed(self.enrollment_id, client=self._client, wait=wait))

    def start(self) -> EnrollmentInstance:
        """Ask for the instance to be started (idempotent); the platform does the work.

        Returns at once with the request (status ``pending``); follow it with
        :meth:`get` or :meth:`wait`.
        """
        from ._generated.api.customer import start_enrollment_instance

        return unwrap(start_enrollment_instance.sync_detailed(self.enrollment_id, client=self._client))

    def stop(self) -> EnrollmentInstance:
        """Ask for the instance to be stopped (idempotent)."""
        from ._generated.api.customer import stop_enrollment_instance

        return unwrap(stop_enrollment_instance.sync_detailed(self.enrollment_id, client=self._client))

    def credentials(self) -> EnrollmentInstanceCredentials:
        """The instance's application key (``.key``), for calling its entries.

        Never part of :meth:`get`; treat it as a secret.
        """
        from ._generated.api.customer import get_enrollment_instance_credentials

        return unwrap(get_enrollment_instance_credentials.sync_detailed(self.enrollment_id, client=self._client))

    def wait(self, *, timeout: float = 300.0, request: EnrollmentInstance | None = None) -> EnrollmentInstance:
        """Wait until the current request has finished and return the instance.

        Returns on ``succeeded`` or ``failed`` (inspect ``status``, ``reason``
        and ``fault``). Raises :class:`TimeoutError` after ``timeout`` seconds.

        Pass the state :meth:`start` or :meth:`stop` returned as ``request`` to wait for *that*
        request: if a newer one replaces it first (``stop`` right after your ``start``, say),
        :class:`~unitysvc.exceptions.InstanceSuperseded` is raised instead of reporting the other
        request's outcome as yours.
        """
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"instance of enrollment {self.enrollment_id} did not finish in {timeout:g}s")
            state = self.get(wait=_poll_seconds(self._client, remaining))
            if request is not None and state.generation != request.generation:
                raise InstanceSuperseded(
                    f"{request.requested_action} #{request.generation} of enrollment {self.enrollment_id} was "
                    f"replaced by {state.requested_action} #{state.generation}"
                )
            if state.status in INSTANCE_FINISHED:
                return state
            time.sleep(1)

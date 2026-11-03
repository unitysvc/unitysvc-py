"""Interactive room chat for terminal clients (``usvc rooms chat``, ``usvc_seller rooms chat``).

:class:`ChatSession` holds the logic and works with any ``AsyncRooms``-shaped
client; :func:`run_chat` puts it in a terminal and needs the ``chat`` extra
(``pip install "unitysvc-py[chat]"``).
"""

from .session import ChatError, ChatSession, RoomsClient, format_message
from .terminal import run_chat

__all__ = ["ChatError", "ChatSession", "RoomsClient", "format_message", "run_chat"]

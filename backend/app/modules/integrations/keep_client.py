"""Thin wrapper around gkeepapi (unofficial Google Keep client).

Isolates the reverse-engineered protocol details to this one file, so drift
in gkeepapi's API only requires changes here, not in KeepSyncService/router.

gkeepapi's ``login``/``sync``/``createList``/``find`` calls are blocking
network I/O (the library has no async support) — every method here is meant
to be called via ``asyncio.to_thread(...)`` from the async service layer so a
slow or broken Keep session never stalls the event loop.
"""

import secrets

import gkeepapi

from app.modules.integrations.exceptions import KeepAuthenticationError, KeepNoteMissingError


def generate_device_id() -> str:
    """Generate a random device ID for a new Keep connection (gkeepapi/gpsoauth require one)."""
    return secrets.token_hex(8)


class KeepClient:
    """Synchronous wrapper around a single gkeepapi.Keep() session."""

    def authenticate(self, email: str, master_token: str, device_id: str) -> gkeepapi.Keep:
        """Log in to Google Keep using a previously-obtained master token.

        Args:
            email: Google account email
            master_token: gpsoauth master token (acts as the account password here)
            device_id: Device ID associated with the master token

        Returns:
            An authenticated gkeepapi.Keep session

        Raises:
            KeepAuthenticationError: If login fails
        """
        keep = gkeepapi.Keep()
        try:
            keep.login(email, master_token, device_id=device_id)
        except Exception as e:
            raise KeepAuthenticationError(f"Google Keep login failed: {e}") from e
        return keep

    def find_or_create_note(self, keep: gkeepapi.Keep, title: str) -> gkeepapi.node.List:
        """Find an existing checklist note by title, or create a new one.

        Args:
            keep: Authenticated Keep session
            title: Note title to search for / create

        Returns:
            The matching or newly-created checklist note
        """
        for node in keep.find(query=title, trashed=False, archived=False):
            if isinstance(node, gkeepapi.node.List) and node.title == title:
                return node
        return keep.createList(title, [])

    def get_note(self, keep: gkeepapi.Keep, note_id: str) -> gkeepapi.node.List:
        """Fetch a previously-created checklist note by its Keep node ID.

        Args:
            keep: Authenticated Keep session
            note_id: Keep node ID (as stored on the mirror)

        Returns:
            The checklist note

        Raises:
            KeepAuthenticationError: If the note no longer exists (e.g. deleted in Keep)
        """
        note = keep.get(note_id)
        if note is None:
            raise KeepNoteMissingError(f"Keep note {note_id} not found (deleted in Keep?)")
        return note

    def rebuild_checklist(self, note: gkeepapi.node.List, lines: list[tuple[str, bool]]) -> None:
        """Replace a checklist note's items with the given lines (full push, no diffing).

        Args:
            note: Checklist note to rebuild
            lines: (text, checked) pairs, in desired order
        """
        for item in list(note.items):
            item.delete()
        for text, checked in lines:
            note.add(text, checked)

    def sync(self, keep: gkeepapi.Keep) -> None:
        """Push local changes to Google Keep's servers.

        Args:
            keep: Authenticated Keep session with pending local changes
        """
        keep.sync()

"""Main GCalClient — the primary interface for the SDK."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .auth import DEFAULT_CREDENTIALS_PATH, DEFAULT_TOKEN_PATH, load_credentials
from .calendars import CalendarsResource
from .events import EventsResource
from .freebusy import FreeBusyResource


class GCalClient:
    """A typed, Pythonic client for the Google Calendar API v3.

    Usage::

        from gcal_sdk import GCalClient

        client = GCalClient()
        events = client.events.list("primary")
        calendars = client.calendars.list()

    By default, credentials are loaded from:
    - ``~/secrets/google-oauth/credentials.json``
    - ``~/secrets/google-oauth/token.json``

    You can override these paths or pass pre-built credentials.
    """

    def __init__(
        self,
        *,
        credentials: Optional[Credentials] = None,
        credentials_path: str | Path = DEFAULT_CREDENTIALS_PATH,
        token_path: str | Path = DEFAULT_TOKEN_PATH,
    ) -> None:
        """Initialize the client.

        Args:
            credentials: Pre-built Google OAuth credentials. If provided,
                credentials_path and token_path are ignored.
            credentials_path: Path to the OAuth client credentials JSON file.
            token_path: Path to the stored token JSON file.
        """
        if credentials is None:
            credentials = load_credentials(
                credentials_path=credentials_path,
                token_path=token_path,
            )

        self._credentials = credentials
        self._service = build("calendar", "v3", credentials=credentials)

        self.events = EventsResource(self._service)
        self.calendars = CalendarsResource(self._service)
        self.freebusy = FreeBusyResource(self._service)

    @property
    def service(self) -> Any:
        """Access the underlying googleapiclient Resource (escape hatch)."""
        return self._service

    @property
    def credentials(self) -> Credentials:
        """Access the underlying OAuth credentials."""
        return self._credentials

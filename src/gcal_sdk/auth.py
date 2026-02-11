"""OAuth credential loading for Google Calendar API."""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar"]

DEFAULT_CREDENTIALS_PATH = "~/secrets/google-oauth/credentials.json"
DEFAULT_TOKEN_PATH = "~/secrets/google-oauth/token.json"


def load_credentials(
    credentials_path: str | Path = DEFAULT_CREDENTIALS_PATH,
    token_path: str | Path = DEFAULT_TOKEN_PATH,
) -> Credentials:
    """Load OAuth credentials from disk, refreshing if expired.

    Args:
        credentials_path: Path to the OAuth client credentials JSON file.
        token_path: Path to the stored token JSON file (with refresh token).

    Returns:
        Valid Google OAuth2 credentials.

    Raises:
        FileNotFoundError: If the token file doesn't exist.
    """
    token_path = Path(os.path.expanduser(str(token_path)))
    credentials_path = Path(os.path.expanduser(str(credentials_path)))

    if not token_path.exists():
        raise FileNotFoundError(
            f"Token file not found: {token_path}. "
            "Run the OAuth flow to generate a token first."
        )

    token_data = json.loads(token_path.read_text())

    # Build credentials from the token file
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", SCOPES),
    )

    # If credentials are expired and we can refresh, do so
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token back to disk
        _save_token(creds, token_path)

    # If we still don't have valid credentials and have a credentials file,
    # try to get client_id/client_secret from there for refresh
    if not creds.valid and creds.refresh_token and credentials_path.exists():
        cred_data = json.loads(credentials_path.read_text())
        # Handle both "installed" and "web" application types
        client_info = cred_data.get("installed") or cred_data.get("web", {})
        if client_info:
            creds = Credentials(
                token=creds.token,
                refresh_token=creds.refresh_token,
                token_uri=client_info.get(
                    "token_uri", "https://oauth2.googleapis.com/token"
                ),
                client_id=client_info.get("client_id"),
                client_secret=client_info.get("client_secret"),
                scopes=SCOPES,
            )
            creds.refresh(Request())
            _save_token(creds, token_path)

    return creds


def _save_token(creds: Credentials, token_path: Path) -> None:
    """Save credentials to the token file."""
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    }
    token_path.write_text(json.dumps(token_data, indent=2))
    token_path.chmod(0o600)

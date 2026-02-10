# gcal-sdk

A clean, typed Python SDK for the Google Calendar API v3. Built on top of `google-api-python-client` with Pydantic v2 models.

## Installation

```bash
pip install gcal-sdk
```

## Authentication

The SDK loads OAuth credentials from default paths:

- `~/secrets/google-oauth/credentials.json` — OAuth client credentials
- `~/secrets/google-oauth/token.json` — refresh token + access token

These paths can be overridden when creating the client.

## Usage

```python
from datetime import datetime, timezone, timedelta
from gcal_sdk import GCalClient

client = GCalClient()

# List upcoming events
events = client.events.list("primary", time_min=datetime.now(timezone.utc))
for event in events:
    print(f"{event.summary} — {event.start}")

# Create an event
start = datetime.now(timezone.utc) + timedelta(hours=1)
end = start + timedelta(hours=1)
new_event = client.events.create(
    "primary",
    summary="Team meeting",
    start=start,
    end=end,
)
print(f"Created: {new_event.html_link}")

# Update an event
updated = client.events.patch(
    "primary",
    event_id=new_event.id,
    summary="Updated team meeting",
)

# Delete an event
client.events.delete("primary", event_id=new_event.id)

# List calendars
calendars = client.calendars.list()
for cal in calendars:
    print(f"{cal.summary} (primary={cal.primary})")

# Get primary calendar
primary = client.calendars.get("primary")

# Check free/busy
busy = client.freebusy.query(
    calendar_ids=["primary"],
    time_min=datetime.now(timezone.utc),
    time_max=datetime.now(timezone.utc) + timedelta(days=1),
)
```

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests (requires valid OAuth tokens)
pytest
```

## License

MIT

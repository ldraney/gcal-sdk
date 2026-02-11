"""Shared test fixtures for gcal-sdk integration tests.

Creates a temporary test calendar for each test session and tears it down
after all tests complete. Tests run against the real Google Calendar API.
"""

import uuid

import pytest

from gcal_sdk import GCalClient


@pytest.fixture(scope="session")
def client() -> GCalClient:
    """Create an authenticated GCalClient for the test session."""
    return GCalClient()


@pytest.fixture(scope="session")
def test_calendar_id(client: GCalClient):
    """Create a temporary test calendar and delete it after the session.

    Yields the calendar ID for use in tests.
    """
    calendar_name = f"gcal-sdk-test-{uuid.uuid4().hex[:8]}"
    calendar = client.calendars.create(summary=calendar_name)
    calendar_id = calendar.id

    yield calendar_id

    # Teardown: delete the test calendar
    try:
        client.calendars.delete(calendar_id)
    except Exception:
        # Best effort cleanup — don't fail tests on teardown errors
        pass

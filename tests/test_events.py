"""Integration tests for event CRUD lifecycle.

Tests run against a real temporary test calendar.
Flow: create -> get -> patch -> list (verify present) -> delete -> list (verify gone)
"""

from datetime import datetime, timedelta, timezone

import pytest

from gcal_sdk import GCalClient


class TestEventCRUD:
    """Full CRUD lifecycle test for events."""

    def test_create_get_update_list_delete(
        self, client: GCalClient, test_calendar_id: str
    ):
        """Test the full event lifecycle: create, get, patch, list, delete."""
        now = datetime.now(timezone.utc)
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=1)

        # --- CREATE ---
        event = client.events.create(
            test_calendar_id,
            summary="SDK Test Event",
            description="Created by gcal-sdk integration tests",
            location="Test Location",
            start=start,
            end=end,
        )
        assert event.id is not None
        assert event.summary == "SDK Test Event"
        assert event.description == "Created by gcal-sdk integration tests"
        assert event.location == "Test Location"
        event_id = event.id

        # --- GET ---
        fetched = client.events.get(test_calendar_id, event_id)
        assert fetched.id == event_id
        assert fetched.summary == "SDK Test Event"

        # --- PATCH (partial update) ---
        patched = client.events.patch(
            test_calendar_id,
            event_id,
            summary="Updated SDK Test Event",
            description="Updated description",
        )
        assert patched.summary == "Updated SDK Test Event"
        assert patched.description == "Updated description"
        # Location should remain unchanged
        assert patched.location == "Test Location"

        # --- LIST (verify event appears) ---
        events = client.events.list(
            test_calendar_id,
            time_min=now,
            time_max=now + timedelta(days=1),
        )
        event_ids = [e.id for e in events]
        assert event_id in event_ids

        # --- DELETE ---
        client.events.delete(test_calendar_id, event_id)

        # --- LIST (verify event is gone) ---
        events_after = client.events.list(
            test_calendar_id,
            time_min=now,
            time_max=now + timedelta(days=1),
        )
        event_ids_after = [e.id for e in events_after]
        assert event_id not in event_ids_after

    def test_create_all_day_event(
        self, client: GCalClient, test_calendar_id: str
    ):
        """Test creating and deleting an all-day event."""
        from datetime import date as date_type

        from gcal_sdk import EventDateTime

        tomorrow = date_type.today() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)

        event = client.events.create(
            test_calendar_id,
            summary="All Day Test",
            body={
                "summary": "All Day Test",
                "start": {"date": tomorrow.isoformat()},
                "end": {"date": day_after.isoformat()},
            },
        )
        assert event.id is not None
        assert event.summary == "All Day Test"

        # Clean up
        client.events.delete(test_calendar_id, event.id)

"""Integration tests for FreeBusy operations."""

from datetime import datetime, timedelta, timezone

from gcal_sdk import GCalClient


class TestFreeBusy:
    """Tests for free/busy queries."""

    def test_query_primary_calendar(self, client: GCalClient):
        """Query free/busy for the primary calendar over next 24 hours."""
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(days=1)

        result = client.freebusy.query(
            calendar_ids=["primary"],
            time_min=now,
            time_max=time_max,
        )

        # Response should have the primary calendar entry
        assert "primary" in result.calendars
        # The busy list might be empty or have entries — both are valid
        assert isinstance(result.calendars["primary"].busy, list)

    def test_query_test_calendar(
        self, client: GCalClient, test_calendar_id: str
    ):
        """Query free/busy for the test calendar."""
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(days=1)

        result = client.freebusy.query(
            calendar_ids=[test_calendar_id],
            time_min=now,
            time_max=time_max,
        )

        assert test_calendar_id in result.calendars
        # Test calendar should be empty (no events created yet in this test)
        assert isinstance(result.calendars[test_calendar_id].busy, list)

    def test_query_multiple_calendars(
        self, client: GCalClient, test_calendar_id: str
    ):
        """Query free/busy for multiple calendars at once."""
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(days=1)

        result = client.freebusy.query(
            calendar_ids=["primary", test_calendar_id],
            time_min=now,
            time_max=time_max,
        )

        assert "primary" in result.calendars
        assert test_calendar_id in result.calendars

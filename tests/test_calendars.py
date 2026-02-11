"""Integration tests for calendar operations."""

from gcal_sdk import GCalClient


class TestCalendars:
    """Tests for calendar listing and retrieval."""

    def test_list_calendars(self, client: GCalClient):
        """List calendars and verify primary calendar exists."""
        calendars = client.calendars.list()
        assert len(calendars) > 0

        # At least one calendar should be the primary
        primary_calendars = [c for c in calendars if c.primary]
        assert len(primary_calendars) == 1
        assert primary_calendars[0].id is not None

    def test_get_primary_calendar(self, client: GCalClient):
        """Get the primary calendar details."""
        primary = client.calendars.get("primary")
        assert primary.id is not None
        assert primary.summary is not None
        assert primary.time_zone is not None
        assert primary.access_role is not None

    def test_test_calendar_exists(
        self, client: GCalClient, test_calendar_id: str
    ):
        """Verify that the test calendar fixture created a calendar."""
        calendars = client.calendars.list()
        cal_ids = [c.id for c in calendars]
        assert test_calendar_id in cal_ids

    def test_get_test_calendar(
        self, client: GCalClient, test_calendar_id: str
    ):
        """Get the test calendar and verify its properties."""
        cal = client.calendars.get(test_calendar_id)
        assert cal.id == test_calendar_id
        assert cal.summary is not None
        assert cal.summary.startswith("gcal-sdk-test-")

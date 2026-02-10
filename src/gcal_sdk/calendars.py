"""Calendars resource wrapper for Google Calendar API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .models import Calendar

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


class CalendarsResource:
    """Provides methods for Google Calendar CalendarList operations."""

    def __init__(self, service: Resource) -> None:
        self._service = service
        self._calendar_list = service.calendarList()
        self._calendars = service.calendars()

    def list(
        self,
        *,
        show_deleted: bool = False,
        show_hidden: bool = False,
        max_results: int = 250,
        page_token: Optional[str] = None,
    ) -> list[Calendar]:
        """List calendars in the user's calendar list.

        Args:
            show_deleted: Whether to show deleted calendars.
            show_hidden: Whether to show hidden calendars.
            max_results: Maximum number of calendars to return.
            page_token: Token for paginated results.

        Returns:
            List of Calendar objects.
        """
        kwargs: dict = {
            "showDeleted": show_deleted,
            "showHidden": show_hidden,
            "maxResults": max_results,
        }
        if page_token is not None:
            kwargs["pageToken"] = page_token

        result = self._calendar_list.list(**kwargs).execute()
        items = result.get("items", [])
        return [Calendar.from_api_response(item) for item in items]

    def list_all(
        self,
        *,
        show_deleted: bool = False,
        show_hidden: bool = False,
    ) -> list[Calendar]:
        """List all calendars, automatically paginating.

        Returns:
            Complete list of Calendar objects across all pages.
        """
        all_calendars: list[Calendar] = []
        page_token: Optional[str] = None

        while True:
            kwargs: dict = {
                "showDeleted": show_deleted,
                "showHidden": show_hidden,
                "maxResults": 250,
            }
            if page_token is not None:
                kwargs["pageToken"] = page_token

            result = self._calendar_list.list(**kwargs).execute()
            items = result.get("items", [])
            all_calendars.extend(Calendar.from_api_response(item) for item in items)

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_calendars

    def get(self, calendar_id: str = "primary") -> Calendar:
        """Get a calendar by ID.

        For CalendarList entries this returns the user's view of the
        calendar (including color, notification settings, etc.).

        Args:
            calendar_id: Calendar identifier (default "primary").

        Returns:
            The Calendar object.
        """
        result = self._calendar_list.get(calendarId=calendar_id).execute()
        return Calendar.from_api_response(result)

    def create(
        self,
        summary: str,
        *,
        description: Optional[str] = None,
        time_zone: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Calendar:
        """Create a new secondary calendar.

        Args:
            summary: Title of the new calendar.
            description: Description of the calendar.
            time_zone: Time zone (e.g. "America/Denver").
            location: Geographic location.

        Returns:
            The created Calendar.
        """
        body: dict = {"summary": summary}
        if description is not None:
            body["description"] = description
        if time_zone is not None:
            body["timeZone"] = time_zone
        if location is not None:
            body["location"] = location

        result = self._calendars.insert(body=body).execute()
        return Calendar.from_api_response(result)

    def delete(self, calendar_id: str) -> None:
        """Delete a secondary calendar.

        Args:
            calendar_id: Calendar identifier. Cannot be "primary".
        """
        self._calendars.delete(calendarId=calendar_id).execute()

    def clear(self, calendar_id: str = "primary") -> None:
        """Clear all events from a calendar.

        Args:
            calendar_id: Calendar identifier.
        """
        self._calendars.clear(calendarId=calendar_id).execute()

"""Events resource wrapper for Google Calendar API."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .models import Event, EventDateTime

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


class EventsResource:
    """Provides methods for Google Calendar Events operations."""

    def __init__(self, service: Resource) -> None:
        self._service = service
        self._events = service.events()

    @staticmethod
    def _build_list_kwargs(
        calendar_id: str,
        *,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 250,
        single_events: bool = True,
        order_by: Optional[str] = "startTime",
        q: Optional[str] = None,
        page_token: Optional[str] = None,
        show_deleted: bool = False,
    ) -> dict:
        """Build kwargs dict for the events().list() API call."""
        kwargs: dict = {
            "calendarId": calendar_id,
            "maxResults": max_results,
            "singleEvents": single_events,
            "showDeleted": show_deleted,
        }
        if time_min is not None:
            kwargs["timeMin"] = _ensure_isoformat(time_min)
        if time_max is not None:
            kwargs["timeMax"] = _ensure_isoformat(time_max)
        if order_by is not None:
            kwargs["orderBy"] = order_by
        if q is not None:
            kwargs["q"] = q
        if page_token is not None:
            kwargs["pageToken"] = page_token
        return kwargs

    def list(
        self,
        calendar_id: str = "primary",
        *,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 250,
        single_events: bool = True,
        order_by: Optional[str] = "startTime",
        q: Optional[str] = None,
        page_token: Optional[str] = None,
        show_deleted: bool = False,
    ) -> list[Event]:
        """List events from a calendar.

        Args:
            calendar_id: Calendar identifier (default "primary").
            time_min: Lower bound (inclusive) for event start time.
            time_max: Upper bound (exclusive) for event start time.
            max_results: Maximum number of events to return.
            single_events: Whether to expand recurring events.
            order_by: Sort order ("startTime" or "updated"). Only valid
                when single_events is True for "startTime".
            q: Free text search query.
            page_token: Token for paginated results.
            show_deleted: Whether to include deleted events.

        Returns:
            List of Event objects.
        """
        kwargs = self._build_list_kwargs(
            calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
            single_events=single_events,
            order_by=order_by,
            q=q,
            page_token=page_token,
            show_deleted=show_deleted,
        )

        result = self._events.list(**kwargs).execute()
        items = result.get("items", [])
        return [Event.from_api_response(item) for item in items]

    def list_all(
        self,
        calendar_id: str = "primary",
        *,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        single_events: bool = True,
        order_by: Optional[str] = "startTime",
        q: Optional[str] = None,
        show_deleted: bool = False,
    ) -> list[Event]:
        """List all events, automatically paginating.

        Same arguments as list() except max_results and page_token.

        Returns:
            Complete list of Event objects across all pages.
        """
        all_events: list[Event] = []
        page_token: Optional[str] = None

        while True:
            kwargs = self._build_list_kwargs(
                calendar_id,
                time_min=time_min,
                time_max=time_max,
                single_events=single_events,
                order_by=order_by,
                q=q,
                page_token=page_token,
                show_deleted=show_deleted,
            )

            result = self._events.list(**kwargs).execute()
            items = result.get("items", [])
            all_events.extend(Event.from_api_response(item) for item in items)

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_events

    def get(self, calendar_id: str, event_id: str) -> Event:
        """Get a single event by ID.

        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.

        Returns:
            The Event object.
        """
        result = (
            self._events.get(calendarId=calendar_id, eventId=event_id).execute()
        )
        return Event.from_api_response(result)

    def create(
        self,
        calendar_id: str = "primary",
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start: Optional[datetime | EventDateTime] = None,
        end: Optional[datetime | EventDateTime] = None,
        attendees: Optional[list[str | dict]] = None,
        recurrence: Optional[list[str]] = None,
        time_zone: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> Event:
        """Create an event on a calendar.

        You can pass a pre-built `body` dict, or use the convenience
        keyword arguments to construct one.

        Args:
            calendar_id: Calendar identifier.
            summary: Event title.
            description: Event description.
            location: Event location.
            start: Start time (datetime or EventDateTime).
            end: End time (datetime or EventDateTime).
            attendees: List of attendee emails or attendee dicts.
            recurrence: List of RRULE strings.
            time_zone: Time zone (e.g. "America/Denver").
            body: Raw event body dict (overrides other fields).

        Returns:
            The created Event.
        """
        body = _build_event_body(
            summary=summary,
            description=description,
            location=location,
            start=start,
            end=end,
            time_zone=time_zone,
            attendees=attendees,
            recurrence=recurrence,
            body=body,
        )

        result = self._events.insert(calendarId=calendar_id, body=body).execute()
        return Event.from_api_response(result)

    def update(
        self,
        calendar_id: str,
        event_id: str,
        *,
        body: dict,
    ) -> Event:
        """Full update (PUT) of an event — replaces the entire resource.

        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.
            body: Complete event body dict.

        Returns:
            The updated Event.
        """
        result = (
            self._events.update(
                calendarId=calendar_id, eventId=event_id, body=body
            ).execute()
        )
        return Event.from_api_response(result)

    def patch(
        self,
        calendar_id: str,
        event_id: str,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start: Optional[datetime | EventDateTime] = None,
        end: Optional[datetime | EventDateTime] = None,
        attendees: Optional[list[str | dict]] = None,
        recurrence: Optional[list[str]] = None,
        time_zone: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> Event:
        """Partial update (PATCH) of an event.

        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.
            summary: New title.
            description: New description.
            location: New location.
            start: New start time.
            end: New end time.
            attendees: New attendee list.
            recurrence: New recurrence rules.
            time_zone: Time zone for start/end.
            body: Raw patch body (overrides other fields).

        Returns:
            The patched Event.
        """
        body = _build_event_body(
            summary=summary,
            description=description,
            location=location,
            start=start,
            end=end,
            time_zone=time_zone,
            attendees=attendees,
            recurrence=recurrence,
            body=body,
        )

        result = (
            self._events.patch(
                calendarId=calendar_id, eventId=event_id, body=body
            ).execute()
        )
        return Event.from_api_response(result)

    def delete(
        self,
        calendar_id: str,
        event_id: str,
        *,
        send_updates: Optional[str] = None,
    ) -> None:
        """Delete an event.

        Args:
            calendar_id: Calendar identifier.
            event_id: Event identifier.
            send_updates: How to send notifications ("all", "externalOnly", "none").
        """
        kwargs: dict = {"calendarId": calendar_id, "eventId": event_id}
        if send_updates is not None:
            kwargs["sendUpdates"] = send_updates
        self._events.delete(**kwargs).execute()

    def move(
        self,
        calendar_id: str,
        event_id: str,
        destination_calendar_id: str,
    ) -> Event:
        """Move an event to another calendar.

        Args:
            calendar_id: Source calendar identifier.
            event_id: Event identifier.
            destination_calendar_id: Destination calendar identifier.

        Returns:
            The moved Event.
        """
        result = (
            self._events.move(
                calendarId=calendar_id,
                eventId=event_id,
                destination=destination_calendar_id,
            ).execute()
        )
        return Event.from_api_response(result)

    def instances(
        self,
        calendar_id: str,
        event_id: str,
        *,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 250,
    ) -> list[Event]:
        """List instances of a recurring event.

        Args:
            calendar_id: Calendar identifier.
            event_id: Recurring event identifier.
            time_min: Lower bound for instance start time.
            time_max: Upper bound for instance start time.
            max_results: Maximum instances to return.

        Returns:
            List of Event instances.
        """
        kwargs: dict = {
            "calendarId": calendar_id,
            "eventId": event_id,
            "maxResults": max_results,
        }
        if time_min is not None:
            kwargs["timeMin"] = _ensure_isoformat(time_min)
        if time_max is not None:
            kwargs["timeMax"] = _ensure_isoformat(time_max)

        result = self._events.instances(**kwargs).execute()
        items = result.get("items", [])
        return [Event.from_api_response(item) for item in items]


def _build_event_body(
    summary: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    start: Optional[datetime | EventDateTime] = None,
    end: Optional[datetime | EventDateTime] = None,
    time_zone: Optional[str] = None,
    attendees: Optional[list[str | dict]] = None,
    recurrence: Optional[list[str]] = None,
    body: Optional[dict] = None,
) -> dict:
    """Build an event body dict from convenience kwargs or a raw body.

    If *body* is provided it is returned as-is (it takes precedence).
    Otherwise a dict is assembled from the individual keyword arguments.
    """
    if body is not None:
        return body

    result: dict = {}
    if summary is not None:
        result["summary"] = summary
    if description is not None:
        result["description"] = description
    if location is not None:
        result["location"] = location
    if start is not None:
        result["start"] = _to_event_datetime(start, time_zone)
    if end is not None:
        result["end"] = _to_event_datetime(end, time_zone)
    if attendees is not None:
        result["attendees"] = [
            {"email": a} if isinstance(a, str) else a for a in attendees
        ]
    if recurrence is not None:
        result["recurrence"] = recurrence
    return result


def _ensure_isoformat(dt: datetime) -> str:
    """Ensure a datetime is in ISO 8601 format with timezone."""
    if dt.tzinfo is None:
        raise ValueError(
            "Datetime must be timezone-aware. Use datetime.now(timezone.utc) "
            "or attach a timezone with .replace(tzinfo=...)."
        )
    return dt.isoformat()


def _to_event_datetime(
    value: datetime | EventDateTime,
    time_zone: Optional[str] = None,
) -> dict:
    """Convert a datetime or EventDateTime to an API-compatible dict."""
    if isinstance(value, EventDateTime):
        return value.to_api_dict()
    # It's a plain datetime — must be timezone-aware
    if value.tzinfo is None:
        raise ValueError(
            "Datetime must be timezone-aware. Use datetime.now(timezone.utc) "
            "or attach a timezone with .replace(tzinfo=...)."
        )
    result: dict = {"dateTime": value.isoformat()}
    if time_zone is not None:
        result["timeZone"] = time_zone
    return result

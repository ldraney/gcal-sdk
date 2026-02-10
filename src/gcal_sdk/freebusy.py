"""FreeBusy resource wrapper for Google Calendar API."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .models import FreeBusyResponse

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


class FreeBusyResource:
    """Provides methods for Google Calendar FreeBusy operations."""

    def __init__(self, service: Resource) -> None:
        self._service = service
        self._freebusy = service.freebusy()

    def query(
        self,
        calendar_ids: list[str],
        time_min: datetime,
        time_max: datetime,
        *,
        time_zone: Optional[str] = None,
        group_expansion_max: Optional[int] = None,
        calendar_expansion_max: Optional[int] = None,
    ) -> FreeBusyResponse:
        """Query free/busy information for a set of calendars.

        Args:
            calendar_ids: List of calendar identifiers to query.
            time_min: Start of the time range.
            time_max: End of the time range.
            time_zone: Time zone (defaults to UTC on the server).
            group_expansion_max: Maximum number of calendar members to
                expand for group calendars.
            calendar_expansion_max: Maximum number of calendars to
                expand for calendar groups.

        Returns:
            FreeBusyResponse with busy periods per calendar.

        Raises:
            ValueError: If datetimes are not timezone-aware.
        """
        if time_min.tzinfo is None or time_max.tzinfo is None:
            raise ValueError(
                "time_min and time_max must be timezone-aware datetimes."
            )

        body: dict = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "items": [{"id": cal_id} for cal_id in calendar_ids],
        }
        if time_zone is not None:
            body["timeZone"] = time_zone
        if group_expansion_max is not None:
            body["groupExpansionMax"] = group_expansion_max
        if calendar_expansion_max is not None:
            body["calendarExpansionMax"] = calendar_expansion_max

        result = self._freebusy.query(body=body).execute()
        return FreeBusyResponse.from_api_response(result)

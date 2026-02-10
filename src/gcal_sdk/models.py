"""Pydantic v2 models for Google Calendar API responses."""

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class EventDateTime(BaseModel):
    """Represents a start or end time for an event.

    Google Calendar uses either `date` (all-day events) or
    `dateTime` + optional `timeZone` (timed events).
    """

    date: Optional[dt.date] = None
    date_time: Optional[dt.datetime] = Field(None, alias="dateTime")
    time_zone: Optional[str] = Field(None, alias="timeZone")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def check_date_or_datetime(self) -> "EventDateTime":
        if self.date is None and self.date_time is None:
            raise ValueError("Either 'date' or 'dateTime' must be set")
        return self

    def to_api_dict(self) -> dict:
        """Convert to the dict format expected by the Google Calendar API."""
        result: dict = {}
        if self.date is not None:
            result["date"] = self.date.isoformat()
        if self.date_time is not None:
            result["dateTime"] = self.date_time.isoformat()
        if self.time_zone is not None:
            result["timeZone"] = self.time_zone
        return result


class Attendee(BaseModel):
    """An event attendee."""

    email: str
    display_name: Optional[str] = Field(None, alias="displayName")
    response_status: Optional[str] = Field(None, alias="responseStatus")
    optional: Optional[bool] = None
    organizer: Optional[bool] = None
    self_: Optional[bool] = Field(None, alias="self")

    model_config = {"populate_by_name": True}


class Event(BaseModel):
    """A Google Calendar event."""

    id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: Optional[EventDateTime] = None
    end: Optional[EventDateTime] = None
    status: Optional[str] = None
    html_link: Optional[str] = Field(None, alias="htmlLink")
    created: Optional[dt.datetime] = None
    updated: Optional[dt.datetime] = None
    creator: Optional[dict] = None
    organizer: Optional[dict] = None
    attendees: Optional[list[Attendee]] = None
    recurrence: Optional[list[str]] = None
    recurring_event_id: Optional[str] = Field(None, alias="recurringEventId")
    transparency: Optional[str] = None
    visibility: Optional[str] = None
    ical_uid: Optional[str] = Field(None, alias="iCalUID")
    sequence: Optional[int] = None
    etag: Optional[str] = None
    kind: Optional[str] = None
    calendar_id: Optional[str] = Field(None, alias="calendarId")
    color_id: Optional[str] = Field(None, alias="colorId")
    hangout_link: Optional[str] = Field(None, alias="hangoutLink")
    conference_data: Optional[dict] = Field(None, alias="conferenceData")
    reminders: Optional[dict] = None
    source: Optional[dict] = None
    extended_properties: Optional[dict] = Field(None, alias="extendedProperties")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_api_response(cls, data: dict) -> "Event":
        """Create an Event from a raw Google Calendar API response dict."""
        return cls.model_validate(data)


class Calendar(BaseModel):
    """A Google Calendar calendar (from CalendarList)."""

    id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    time_zone: Optional[str] = Field(None, alias="timeZone")
    primary: bool = False
    access_role: Optional[str] = Field(None, alias="accessRole")
    background_color: Optional[str] = Field(None, alias="backgroundColor")
    foreground_color: Optional[str] = Field(None, alias="foregroundColor")
    selected: Optional[bool] = None
    hidden: Optional[bool] = None
    deleted: Optional[bool] = None
    etag: Optional[str] = None
    kind: Optional[str] = None
    color_id: Optional[str] = Field(None, alias="colorId")
    summary_override: Optional[str] = Field(None, alias="summaryOverride")
    notification_settings: Optional[dict] = Field(None, alias="notificationSettings")
    conference_properties: Optional[dict] = Field(None, alias="conferenceProperties")
    default_reminders: Optional[list[dict]] = Field(None, alias="defaultReminders")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_api_response(cls, data: dict) -> "Calendar":
        """Create a Calendar from a raw Google Calendar API response dict."""
        return cls.model_validate(data)


class BusyPeriod(BaseModel):
    """A period during which a calendar is busy."""

    start: dt.datetime
    end: dt.datetime


class CalendarFreeBusy(BaseModel):
    """Free/busy information for a single calendar."""

    busy: list[BusyPeriod] = Field(default_factory=list)
    errors: Optional[list[dict]] = None


class FreeBusyResponse(BaseModel):
    """Response from a free/busy query."""

    kind: Optional[str] = None
    time_min: Optional[dt.datetime] = Field(None, alias="timeMin")
    time_max: Optional[dt.datetime] = Field(None, alias="timeMax")
    calendars: dict[str, CalendarFreeBusy] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @classmethod
    def from_api_response(cls, data: dict) -> "FreeBusyResponse":
        """Create a FreeBusyResponse from a raw Google Calendar API response dict."""
        return cls.model_validate(data)

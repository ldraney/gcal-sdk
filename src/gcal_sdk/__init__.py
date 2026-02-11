"""gcal-sdk: A clean, typed Python SDK for the Google Calendar API v3."""

from .auth import load_credentials
from .client import GCalClient
from .models import (
    Attendee,
    BusyPeriod,
    Calendar,
    CalendarFreeBusy,
    Event,
    EventDateTime,
    FreeBusyResponse,
)

__version__ = "0.1.0"

__all__ = [
    "GCalClient",
    "load_credentials",
    "Event",
    "EventDateTime",
    "Attendee",
    "Calendar",
    "BusyPeriod",
    "CalendarFreeBusy",
    "FreeBusyResponse",
]

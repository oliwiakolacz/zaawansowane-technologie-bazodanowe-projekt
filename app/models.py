from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Conference:
    conference_id: int
    name: str
    start_date: date
    end_date: date
    location: str
    max_attendees: int
    status: str


@dataclass(frozen=True)
class Track:
    track_id: int
    conference_id: int
    name: str
    description: Optional[str]


@dataclass(frozen=True)
class Room:
    room_id: int
    name: str
    capacity: int
    floor: int
    has_projector: bool


@dataclass(frozen=True)
class Speaker:
    speaker_id: int
    first_name: str
    last_name: str
    email: str
    country: Optional[str]
    company: Optional[str]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class Attendee:
    attendee_id: int
    first_name: str
    last_name: str
    email: str
    company: Optional[str]
    registration_date: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class TicketType:
    ticket_type_id: int
    conference_id: int
    name: str
    price: Decimal
    max_quantity: int
    sales_start: date
    sales_end: date


@dataclass(frozen=True)
class Session:
    session_id: int
    conference_id: int
    track_id: Optional[int]
    room_id: int
    speaker_id: int
    title: str
    start_time: datetime
    end_time: datetime
    session_type: str
    difficulty_level: str


@dataclass(frozen=True)
class Ticket:
    ticket_id: int
    ticket_type_id: int
    attendee_id: int
    purchase_date: datetime
    price: Decimal
    status: str
    qr_code: str


@dataclass(frozen=True)
class SessionRegistration:
    registration_id: int
    session_id: int
    attendee_id: int
    registration_date: datetime
    status: str

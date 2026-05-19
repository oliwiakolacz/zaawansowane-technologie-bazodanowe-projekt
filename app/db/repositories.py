from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

import pandas as pd

from db.connection import ConnectionManager
from models import (
    Attendee,
    Conference,
    Room,
    Session,
    Speaker,
    Ticket,
    TicketType,
    Track,
)


class ConferenceRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[Conference]:
        sql = """
            SELECT ConferenceID, Name, StartDate, EndDate, Location, MaxAttendees, Status
            FROM Conferences
            ORDER BY StartDate DESC
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [Conference(*row) for row in cur.fetchall()]

    def get(self, conference_id: int) -> Optional[Conference]:
        sql = """
            SELECT ConferenceID, Name, StartDate, EndDate, Location, MaxAttendees, Status
            FROM Conferences WHERE ConferenceID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, conference_id)
            row = cur.fetchone()
            return Conference(*row) if row else None

    def create(self, name: str, start_date: date, end_date: date, location: str,
               max_attendees: int, status: str) -> int:
        sql = """
            INSERT INTO Conferences (Name, StartDate, EndDate, Location, MaxAttendees, Status)
            OUTPUT INSERTED.ConferenceID
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, name, start_date, end_date, location, max_attendees, status)
            return int(cur.fetchval())

    def update(self, conference_id: int, name: str, start_date: date, end_date: date,
               location: str, max_attendees: int, status: str) -> None:
        sql = """
            UPDATE Conferences
            SET Name = ?, StartDate = ?, EndDate = ?, Location = ?,
                MaxAttendees = ?, Status = ?
            WHERE ConferenceID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, name, start_date, end_date, location, max_attendees, status, conference_id)

    def delete(self, conference_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM Conferences WHERE ConferenceID = ?", conference_id)


class TicketTypeRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[TicketType]:
        sql = """
            SELECT TicketTypeID, ConferenceID, Name, Price, MaxQuantity, SalesStart, SalesEnd
            FROM TicketTypes
            ORDER BY ConferenceID, Price
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [TicketType(*row) for row in cur.fetchall()]

    def list_for_conference(self, conference_id: int) -> List[TicketType]:
        sql = """
            SELECT TicketTypeID, ConferenceID, Name, Price, MaxQuantity, SalesStart, SalesEnd
            FROM TicketTypes
            WHERE ConferenceID = ?
            ORDER BY Price
        """
        with self._conn.query() as cur:
            cur.execute(sql, conference_id)
            return [TicketType(*row) for row in cur.fetchall()]

    def availability(self, ticket_type_id: int) -> dict:
        sql = """
            SELECT
                tt.MaxQuantity,
                (SELECT COUNT(*) FROM Tickets t
                 WHERE t.TicketTypeID = tt.TicketTypeID
                   AND t.Status IN ('Active', 'Used')) AS Sold
            FROM TicketTypes tt
            WHERE tt.TicketTypeID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, ticket_type_id)
            row = cur.fetchone()
            if not row:
                return {"max": 0, "sold": 0, "available": 0}
            return {
                "max": row[0],
                "sold": row[1],
                "available": row[0] - row[1],
            }

    def create(self, conference_id: int, name: str, price: Decimal, max_quantity: int,
               sales_start: date, sales_end: date) -> int:
        sql = """
            INSERT INTO TicketTypes (ConferenceID, Name, Price, MaxQuantity, SalesStart, SalesEnd)
            OUTPUT INSERTED.TicketTypeID
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, conference_id, name, price, max_quantity, sales_start, sales_end)
            return int(cur.fetchval())

    def update(self, ticket_type_id: int, conference_id: int, name: str, price: Decimal,
               max_quantity: int, sales_start: date, sales_end: date) -> None:
        sql = """
            UPDATE TicketTypes
            SET ConferenceID = ?, Name = ?, Price = ?, MaxQuantity = ?,
                SalesStart = ?, SalesEnd = ?
            WHERE TicketTypeID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, conference_id, name, price, max_quantity,
                        sales_start, sales_end, ticket_type_id)

    def delete(self, ticket_type_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM TicketTypes WHERE TicketTypeID = ?", ticket_type_id)


class AttendeeRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[Attendee]:
        sql = """
            SELECT AttendeeID, FirstName, LastName, Email, Company, RegistrationDate
            FROM Attendees
            ORDER BY LastName, FirstName
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [Attendee(*row) for row in cur.fetchall()]

    def list_with_valid_ticket(self, conference_id: int) -> List[Attendee]:
        sql = """
            SELECT DISTINCT a.AttendeeID, a.FirstName, a.LastName, a.Email, a.Company, a.RegistrationDate
            FROM Attendees a
            JOIN Tickets t ON t.AttendeeID = a.AttendeeID
            JOIN TicketTypes tt ON tt.TicketTypeID = t.TicketTypeID
            WHERE tt.ConferenceID = ?
              AND t.Status IN ('Active', 'Used')
            ORDER BY a.LastName, a.FirstName
        """
        with self._conn.query() as cur:
            cur.execute(sql, conference_id)
            return [Attendee(*row) for row in cur.fetchall()]

    def get(self, attendee_id: int) -> Optional[Attendee]:
        sql = """
            SELECT AttendeeID, FirstName, LastName, Email, Company, RegistrationDate
            FROM Attendees WHERE AttendeeID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, attendee_id)
            row = cur.fetchone()
            return Attendee(*row) if row else None

    def create(self, first_name: str, last_name: str, email: str,
               company: Optional[str]) -> int:
        sql = """
            INSERT INTO Attendees (FirstName, LastName, Email, Company)
            OUTPUT INSERTED.AttendeeID
            VALUES (?, ?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, first_name, last_name, email, company)
            return int(cur.fetchval())

    def update(self, attendee_id: int, first_name: str, last_name: str,
               email: str, company: Optional[str]) -> None:
        sql = """
            UPDATE Attendees
            SET FirstName = ?, LastName = ?, Email = ?, Company = ?
            WHERE AttendeeID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, first_name, last_name, email, company, attendee_id)

    def delete(self, attendee_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM Attendees WHERE AttendeeID = ?", attendee_id)


class SessionRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[Session]:
        sql = """
            SELECT SessionID, ConferenceID, TrackID, RoomID, SpeakerID, Title,
                   StartTime, EndTime, SessionType, DifficultyLevel
            FROM Sessions
            ORDER BY StartTime
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [Session(*row) for row in cur.fetchall()]

    def list_for_conference(self, conference_id: int) -> List[Session]:
        sql = """
            SELECT SessionID, ConferenceID, TrackID, RoomID, SpeakerID, Title,
                   StartTime, EndTime, SessionType, DifficultyLevel
            FROM Sessions
            WHERE ConferenceID = ?
            ORDER BY StartTime
        """
        with self._conn.query() as cur:
            cur.execute(sql, conference_id)
            return [Session(*row) for row in cur.fetchall()]

    def get(self, session_id: int) -> Optional[Session]:
        sql = """
            SELECT SessionID, ConferenceID, TrackID, RoomID, SpeakerID, Title,
                   StartTime, EndTime, SessionType, DifficultyLevel
            FROM Sessions WHERE SessionID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, session_id)
            row = cur.fetchone()
            return Session(*row) if row else None

    def schedule_dataframe(self, conference_id: int) -> pd.DataFrame:
        sql = "SELECT * FROM vw_SessionSchedule WHERE ConferenceID = ? ORDER BY StartTime"
        with self._conn.query() as cur:
            cur.execute(sql, conference_id)
            columns = [c[0] for c in cur.description]
            rows = cur.fetchall()
            return pd.DataFrame.from_records(rows, columns=columns)

    def popularity_dataframe(self) -> pd.DataFrame:
        sql = "SELECT * FROM vw_PopularSessions ORDER BY UtilizationPct DESC"
        with self._conn.query() as cur:
            cur.execute(sql)
            columns = [c[0] for c in cur.description]
            rows = cur.fetchall()
            return pd.DataFrame.from_records(rows, columns=columns)

    def has_room_conflict(self, room_id: int, start_time: datetime, end_time: datetime,
                          exclude_session_id: Optional[int] = None) -> Optional[Session]:
        sql = """
            SELECT TOP 1 SessionID, ConferenceID, TrackID, RoomID, SpeakerID, Title,
                   StartTime, EndTime, SessionType, DifficultyLevel
            FROM Sessions
            WHERE RoomID = ?
              AND StartTime < ?
              AND EndTime > ?
              AND (? IS NULL OR SessionID <> ?)
        """
        with self._conn.query() as cur:
            cur.execute(sql, room_id, end_time, start_time,
                        exclude_session_id, exclude_session_id)
            row = cur.fetchone()
            return Session(*row) if row else None

    def create(self, conference_id: int, track_id: Optional[int], room_id: int,
               speaker_id: int, title: str, start_time: datetime, end_time: datetime,
               session_type: str, difficulty_level: str) -> int:
        sql = """
            INSERT INTO Sessions (ConferenceID, TrackID, RoomID, SpeakerID, Title,
                                  StartTime, EndTime, SessionType, DifficultyLevel)
            OUTPUT INSERTED.SessionID
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, conference_id, track_id, room_id, speaker_id, title,
                        start_time, end_time, session_type, difficulty_level)
            return int(cur.fetchval())

    def update(self, session_id: int, conference_id: int, track_id: Optional[int],
               room_id: int, speaker_id: int, title: str, start_time: datetime,
               end_time: datetime, session_type: str, difficulty_level: str) -> None:
        sql = """
            UPDATE Sessions
            SET ConferenceID = ?, TrackID = ?, RoomID = ?, SpeakerID = ?, Title = ?,
                StartTime = ?, EndTime = ?, SessionType = ?, DifficultyLevel = ?
            WHERE SessionID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, conference_id, track_id, room_id, speaker_id, title,
                        start_time, end_time, session_type, difficulty_level, session_id)

    def update_room(self, session_id: int, new_room_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute(
                "UPDATE Sessions SET RoomID = ? WHERE SessionID = ?",
                new_room_id, session_id,
            )

    def delete(self, session_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM Sessions WHERE SessionID = ?", session_id)


class TicketRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_for_attendee(self, attendee_id: int) -> List[Ticket]:
        sql = """
            SELECT TicketID, TicketTypeID, AttendeeID, PurchaseDate, Price, Status, QRCode
            FROM Tickets
            WHERE AttendeeID = ?
            ORDER BY PurchaseDate DESC
        """
        with self._conn.query() as cur:
            cur.execute(sql, attendee_id)
            return [Ticket(*row) for row in cur.fetchall()]

    def get(self, ticket_id: int) -> Optional[Ticket]:
        sql = """
            SELECT TicketID, TicketTypeID, AttendeeID, PurchaseDate, Price, Status, QRCode
            FROM Tickets WHERE TicketID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, ticket_id)
            row = cur.fetchone()
            return Ticket(*row) if row else None


class RoomRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[Room]:
        sql = """
            SELECT RoomID, Name, Capacity, Floor, HasProjector
            FROM Rooms
            ORDER BY Name
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [Room(*row) for row in cur.fetchall()]

    def get(self, room_id: int) -> Optional[Room]:
        sql = """
            SELECT RoomID, Name, Capacity, Floor, HasProjector
            FROM Rooms WHERE RoomID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, room_id)
            row = cur.fetchone()
            return Room(*row) if row else None

    def create(self, name: str, capacity: int, floor: int, has_projector: bool) -> int:
        sql = """
            INSERT INTO Rooms (Name, Capacity, Floor, HasProjector)
            OUTPUT INSERTED.RoomID
            VALUES (?, ?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, name, capacity, floor, 1 if has_projector else 0)
            return int(cur.fetchval())

    def update(self, room_id: int, name: str, capacity: int, floor: int,
               has_projector: bool) -> None:
        sql = """
            UPDATE Rooms
            SET Name = ?, Capacity = ?, Floor = ?, HasProjector = ?
            WHERE RoomID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, name, capacity, floor, 1 if has_projector else 0, room_id)

    def delete(self, room_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM Rooms WHERE RoomID = ?", room_id)


class SpeakerRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[Speaker]:
        sql = """
            SELECT SpeakerID, FirstName, LastName, Email, Country, Company
            FROM Speakers
            ORDER BY LastName, FirstName
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [Speaker(*row) for row in cur.fetchall()]

    def get(self, speaker_id: int) -> Optional[Speaker]:
        sql = """
            SELECT SpeakerID, FirstName, LastName, Email, Country, Company
            FROM Speakers WHERE SpeakerID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, speaker_id)
            row = cur.fetchone()
            return Speaker(*row) if row else None

    def create(self, first_name: str, last_name: str, email: str,
               country: Optional[str], company: Optional[str]) -> int:
        sql = """
            INSERT INTO Speakers (FirstName, LastName, Email, Country, Company)
            OUTPUT INSERTED.SpeakerID
            VALUES (?, ?, ?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, first_name, last_name, email, country, company)
            return int(cur.fetchval())

    def update(self, speaker_id: int, first_name: str, last_name: str, email: str,
               country: Optional[str], company: Optional[str]) -> None:
        sql = """
            UPDATE Speakers
            SET FirstName = ?, LastName = ?, Email = ?, Country = ?, Company = ?
            WHERE SpeakerID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, first_name, last_name, email, country, company, speaker_id)

    def delete(self, speaker_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM Speakers WHERE SpeakerID = ?", speaker_id)


class TrackRepository:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def list_all(self) -> List[Track]:
        sql = """
            SELECT TrackID, ConferenceID, Name, Description
            FROM Tracks
            ORDER BY ConferenceID, Name
        """
        with self._conn.query() as cur:
            cur.execute(sql)
            return [Track(*row) for row in cur.fetchall()]

    def list_for_conference(self, conference_id: int) -> List[Track]:
        sql = """
            SELECT TrackID, ConferenceID, Name, Description
            FROM Tracks
            WHERE ConferenceID = ?
            ORDER BY Name
        """
        with self._conn.query() as cur:
            cur.execute(sql, conference_id)
            return [Track(*row) for row in cur.fetchall()]

    def get(self, track_id: int) -> Optional[Track]:
        sql = """
            SELECT TrackID, ConferenceID, Name, Description
            FROM Tracks WHERE TrackID = ?
        """
        with self._conn.query() as cur:
            cur.execute(sql, track_id)
            row = cur.fetchone()
            return Track(*row) if row else None

    def create(self, conference_id: int, name: str, description: Optional[str]) -> int:
        sql = """
            INSERT INTO Tracks (ConferenceID, Name, Description)
            OUTPUT INSERTED.TrackID
            VALUES (?, ?, ?)
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, conference_id, name, description)
            return int(cur.fetchval())

    def update(self, track_id: int, conference_id: int, name: str,
               description: Optional[str]) -> None:
        sql = """
            UPDATE Tracks
            SET ConferenceID = ?, Name = ?, Description = ?
            WHERE TrackID = ?
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, conference_id, name, description, track_id)

    def delete(self, track_id: int) -> None:
        with self._conn.transaction() as cur:
            cur.execute("DELETE FROM Tracks WHERE TrackID = ?", track_id)

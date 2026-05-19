from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from db.connection import ConnectionManager


class TicketService:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def purchase(self, ticket_type_id: int, attendee_id: int) -> int:
        sql = """
            SET NOCOUNT ON;
            DECLARE @NewTicketID INT;
            EXEC usp_PurchaseTicket ?, ?, @NewTicketID OUTPUT;
            SELECT @NewTicketID;
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, ticket_type_id, attendee_id)
            return int(cur.fetchval())

    def cancel(self, ticket_id: int) -> None:
        get_ticket_sql = """
            SELECT tt.ConferenceID, t.AttendeeID
            FROM Tickets t
            JOIN TicketTypes tt ON tt.TicketTypeID = t.TicketTypeID
            WHERE t.TicketID = ?
        """
        cancel_ticket_sql = """
            UPDATE Tickets
            SET Status = 'Cancelled'
            WHERE TicketID = ? AND Status IN ('Active', 'Used')
        """
        cancel_registrations_sql = """
            UPDATE SessionRegistrations
            SET Status = 'Cancelled'
            WHERE AttendeeID = ?
              AND Status IN ('Confirmed', 'Waitlist')
              AND SessionID IN (
                  SELECT SessionID FROM Sessions WHERE ConferenceID = ?
              )
        """
        with self._conn.transaction() as cur:
            cur.execute(get_ticket_sql, ticket_id)
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Bilet o ID {ticket_id} nie istnieje.")
            conference_id, attendee_id = row[0], row[1]

            cur.execute(cancel_ticket_sql, ticket_id)
            if cur.rowcount == 0:
                raise ValueError("Bilet już anulowany lub w stanie, którego nie można anulować.")

            cur.execute(cancel_registrations_sql, attendee_id, conference_id)

    def update_price(self, ticket_type_id: int, new_price: Decimal) -> None:
        sql = "UPDATE TicketTypes SET Price = ? WHERE TicketTypeID = ?"
        with self._conn.transaction() as cur:
            cur.execute(sql, new_price, ticket_type_id)
            if cur.rowcount == 0:
                raise ValueError(f"Typ biletu o ID {ticket_type_id} nie istnieje.")


class RegistrationService:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def register(self, session_id: int, attendee_id: int) -> str:
        sql = """
            SET NOCOUNT ON;
            DECLARE @AssignedStatus NVARCHAR(20);
            EXEC usp_RegisterForSession ?, ?, @AssignedStatus OUTPUT;
            SELECT @AssignedStatus;
        """
        with self._conn.transaction() as cur:
            cur.execute(sql, session_id, attendee_id)
            return str(cur.fetchval())


class AdminService:
    def __init__(self, connection: ConnectionManager):
        self._conn = connection

    def reassign_session(self, session_id: int, new_room_id: int) -> None:
        get_session_sql = """
            SELECT StartTime, EndTime FROM Sessions WHERE SessionID = ?
        """
        conflict_check_sql = """
            SELECT TOP 1 SessionID, Title
            FROM Sessions
            WHERE RoomID = ?
              AND SessionID <> ?
              AND StartTime < ?
              AND EndTime > ?
        """
        update_sql = "UPDATE Sessions SET RoomID = ? WHERE SessionID = ?"

        with self._conn.transaction() as cur:
            cur.execute(get_session_sql, session_id)
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Sesja o ID {session_id} nie istnieje.")
            start_time, end_time = row[0], row[1]

            cur.execute(conflict_check_sql, new_room_id, session_id, end_time, start_time)
            conflict = cur.fetchone()
            if conflict is not None:
                conflict_session_id, conflict_title = conflict[0], conflict[1]
                raise ValueError(
                    f"Sala zajęta w tym czasie przez sesję #{conflict_session_id} \"{conflict_title}\"."
                )

            cur.execute(update_sql, new_room_id, session_id)

    def conference_report(self, conference_id: int) -> dict:
        overview_sql = """
            SELECT
                c.ConferenceID,
                c.Name AS ConferenceName,
                c.StartDate,
                c.EndDate,
                c.Location,
                c.MaxAttendees,
                c.Status,
                (SELECT COUNT(*) FROM Sessions s WHERE s.ConferenceID = c.ConferenceID) AS SessionsCount,
                (SELECT COUNT(*) FROM TicketTypes tt WHERE tt.ConferenceID = c.ConferenceID) AS TicketTypesCount,
                (SELECT COUNT(*) FROM Tickets t
                  JOIN TicketTypes tt ON tt.TicketTypeID = t.TicketTypeID
                  WHERE tt.ConferenceID = c.ConferenceID
                    AND t.Status IN ('Active', 'Used')) AS TicketsSold,
                (SELECT ISNULL(SUM(t.Price), 0) FROM Tickets t
                  JOIN TicketTypes tt ON tt.TicketTypeID = t.TicketTypeID
                  WHERE tt.ConferenceID = c.ConferenceID
                    AND t.Status IN ('Active', 'Used')) AS TotalRevenue
            FROM Conferences c
            WHERE c.ConferenceID = ?
        """
        tickets_sql = """
            SELECT
                tt.Name AS TicketTypeName,
                tt.Price AS UnitPrice,
                tt.MaxQuantity,
                COUNT(t.TicketID) AS Sold,
                ISNULL(SUM(t.Price), 0) AS Revenue
            FROM TicketTypes tt
            LEFT JOIN Tickets t
                ON t.TicketTypeID = tt.TicketTypeID
               AND t.Status IN ('Active', 'Used')
            WHERE tt.ConferenceID = ?
            GROUP BY tt.TicketTypeID, tt.Name, tt.Price, tt.MaxQuantity
            ORDER BY Revenue DESC
        """
        top_sessions_sql = """
            SELECT TOP 5
                s.Title,
                CONCAT(sp.FirstName, ' ', sp.LastName) AS SpeakerName,
                r.Name AS RoomName,
                r.Capacity,
                COUNT(sr.RegistrationID) AS RegistrationsCount,
                CAST(
                    CASE WHEN r.Capacity = 0 THEN 0
                         ELSE 100.0 * COUNT(sr.RegistrationID) / r.Capacity
                    END AS DECIMAL(5,1)
                ) AS UtilizationPct
            FROM Sessions s
            JOIN Rooms r ON r.RoomID = s.RoomID
            JOIN Speakers sp ON sp.SpeakerID = s.SpeakerID
            LEFT JOIN SessionRegistrations sr
                ON sr.SessionID = s.SessionID
               AND sr.Status IN ('Confirmed', 'Attended')
            WHERE s.ConferenceID = ?
            GROUP BY s.SessionID, s.Title, sp.FirstName, sp.LastName, r.Name, r.Capacity
            ORDER BY RegistrationsCount DESC
        """

        with self._conn.query() as cur:
            cur.execute(overview_sql, conference_id)
            overview_cols = [c[0] for c in cur.description]
            overview = [dict(zip(overview_cols, row)) for row in cur.fetchall()]

            cur.execute(tickets_sql, conference_id)
            tickets_cols = [c[0] for c in cur.description]
            tickets = [dict(zip(tickets_cols, row)) for row in cur.fetchall()]

            cur.execute(top_sessions_sql, conference_id)
            top_cols = [c[0] for c in cur.description]
            top_sessions = [dict(zip(top_cols, row)) for row in cur.fetchall()]

            return {
                "overview": overview,
                "tickets": tickets,
                "top_sessions": top_sessions,
            }

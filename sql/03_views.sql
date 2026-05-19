-- Projekt: ConferenceDB - System zarzadzania konferencjami
-- Opis:    Definiuje 2 widoki pokrywajace najczestsze potrzeby informacyjne:
--          - vw_SessionSchedule: pelny harmonogram sesji (5 JOIN-ow)
--          - vw_PopularSessions: sesje wg popularnosci (GROUP BY i agregaty)

USE ConferenceDB;
GO

-- Widok 1: vw_SessionSchedule
-- Pelny harmonogram sesji ze wszystkimi powiazaniami (konferencja, sala,
-- prelegent, track). Wykorzystuje INNER JOIN dla tabel obowiazkowych
-- oraz LEFT JOIN dla Tracks (track jest moze byc null).

IF OBJECT_ID('vw_SessionSchedule', 'V') IS NOT NULL
    DROP VIEW vw_SessionSchedule;
GO

CREATE VIEW vw_SessionSchedule AS
SELECT
    c.ConferenceID,
    c.Name                                             AS ConferenceName,
    s.SessionID,
    s.Title                                            AS SessionTitle,
    s.StartTime,
    s.EndTime,
    DATEDIFF(MINUTE, s.StartTime, s.EndTime)           AS DurationMinutes,
    s.SessionType,
    s.DifficultyLevel,
    t.Name                                             AS TrackName,
    r.Name                                             AS RoomName,
    r.Capacity                                         AS RoomCapacity,
    r.Floor                                            AS RoomFloor,
    CONCAT(sp.FirstName, ' ', sp.LastName)             AS SpeakerName,
    sp.Company                                         AS SpeakerCompany,
    sp.Country                                         AS SpeakerCountry
FROM Sessions s
INNER JOIN Conferences c ON s.ConferenceID = c.ConferenceID
INNER JOIN Rooms       r ON s.RoomID       = r.RoomID
INNER JOIN Speakers    sp ON s.SpeakerID    = sp.SpeakerID
LEFT  JOIN Tracks      t ON s.TrackID      = t.TrackID;
GO

PRINT 'Widok vw_SessionSchedule zostal utworzony';
GO

-- Widok 2: vw_PopularSessions
-- Statystyki popularnosci sesji z rozbiciem na statusy zapisow oraz
-- procentowym wypelnieniem sali. Wykorzystuje GROUP BY, agregaty (SUM, COUNT),
-- CASE WHEN, NULLIF (zabezpieczenie przed dzieleniem przez zero) i CAST.

IF OBJECT_ID('vw_PopularSessions', 'V') IS NOT NULL
    DROP VIEW vw_PopularSessions;
GO

CREATE VIEW vw_PopularSessions AS
SELECT
    s.SessionID,
    s.Title                                            AS SessionTitle,
    c.Name                                             AS ConferenceName,
    CONCAT(sp.FirstName, ' ', sp.LastName)             AS SpeakerName,
    r.Name                                             AS RoomName,
    r.Capacity                                         AS RoomCapacity,
    COUNT(sr.RegistrationID)                           AS TotalRegistrations,
    SUM(CASE WHEN sr.Status = 'Confirmed' THEN 1 ELSE 0 END) AS ConfirmedCount,
    SUM(CASE WHEN sr.Status = 'Waitlist'  THEN 1 ELSE 0 END) AS WaitlistCount,
    SUM(CASE WHEN sr.Status = 'Cancelled' THEN 1 ELSE 0 END) AS CancelledCount,
    SUM(CASE WHEN sr.Status = 'Attended'  THEN 1 ELSE 0 END) AS AttendedCount,
    CAST(
        100.0 * SUM(CASE WHEN sr.Status IN ('Confirmed','Attended') THEN 1 ELSE 0 END)
        / NULLIF(r.Capacity, 0)
    AS DECIMAL(5,1))                                   AS UtilizationPct
FROM Sessions s
INNER JOIN Conferences c          ON s.ConferenceID = c.ConferenceID
INNER JOIN Speakers    sp         ON s.SpeakerID    = sp.SpeakerID
INNER JOIN Rooms       r          ON s.RoomID       = r.RoomID
LEFT  JOIN SessionRegistrations sr ON s.SessionID    = sr.SessionID
GROUP BY
    s.SessionID, s.Title, c.Name,
    sp.FirstName, sp.LastName,
    r.Name, r.Capacity;
GO

PRINT 'Widok vw_PopularSessions zostal utworzony';
GO

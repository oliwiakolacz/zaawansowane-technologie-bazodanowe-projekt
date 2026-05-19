-- Projekt: ConferenceDB - System zarzadzania konferencjami
-- Opis:    2 triggery realizujace kluczowe scenariusze biznesowe:
--          - trg_AutoWaitlist:        auto-przeniesienie na liste rezerwowa
--                                     gdy sala jest pelna
--          - trg_PriceHistoryAudit:   sledzenie zmian cen biletow

USE ConferenceDB;
GO

-- Trigger 1: trg_AutoWaitlist
-- AFTER INSERT na SessionRegistrations
-- 
-- Jezeli liczba zapisow ze statusem 'Confirmed' na danej sesji
-- przekracza pojemnosc sali, nowy zapis jest automatycznie zmieniany
-- na 'Waitlist'. Niezalezna od procedury usp_RegisterForSession
-- dziala nawet przy bezposrednim INSERT z aplikacji.

IF OBJECT_ID('trg_AutoWaitlist', 'TR') IS NOT NULL
    DROP TRIGGER trg_AutoWaitlist;
GO

CREATE TRIGGER trg_AutoWaitlist
ON SessionRegistrations
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE sr
    SET sr.Status = 'Waitlist'
    FROM SessionRegistrations sr
    INNER JOIN inserted   i ON sr.RegistrationID = i.RegistrationID
    INNER JOIN Sessions   s ON i.SessionID       = s.SessionID
    INNER JOIN Rooms      r ON s.RoomID          = r.RoomID
    WHERE i.Status = 'Confirmed'
      AND (
          SELECT COUNT(*)
          FROM SessionRegistrations sr2
          WHERE sr2.SessionID = i.SessionID
            AND sr2.Status = 'Confirmed'
      ) > r.Capacity;
END;
GO

PRINT 'Utworzono trigger trg_AutoWaitlist';
GO

-- Trigger 2: trg_PriceHistoryAudit
-- AFTER UPDATE na TicketTypes
-- 
-- Jezeli kolumna Price zostala zaktualizowana, do tabeli PriceHistory
-- trafia para (stara cena, nowa cena) wraz z timestampem (DEFAULT) i nazwa
-- uzytkownika SQL (DEFAULT SUSER_SNAME()). 

IF OBJECT_ID('trg_PriceHistoryAudit', 'TR') IS NOT NULL
    DROP TRIGGER trg_PriceHistoryAudit;
GO

CREATE TRIGGER trg_PriceHistoryAudit
ON TicketTypes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Wczesne wyjscie jezeli Price nie byl modyfikowany
    -- (UPDATE na innych kolumnach nie powinien go wykonywac)
    IF NOT UPDATE(Price)
        RETURN;

    INSERT INTO PriceHistory (TicketTypeID, OldPrice, NewPrice, ChangedBy)
    SELECT
        i.TicketTypeID,
        d.Price,
        i.Price,
        SUSER_SNAME()
    FROM inserted i
    INNER JOIN deleted d ON i.TicketTypeID = d.TicketTypeID
    WHERE i.Price <> d.Price;
    -- Filtr i.Price <> d.Price chroni przed "pustym update"
    -- gdy kolumna Price byla zaktualizowana ale wartosc nie ulegla zmianie
END;
GO

PRINT 'Utworzono trigger trg_PriceHistoryAudit';
GO

-- Projekt: ConferenceDB - System zarzadzania konferencjami
-- Opis:    2 procedury operacyjne systemu:
--          - usp_PurchaseTicket:      kupno biletu z walidacja okna sprzedazy
--          - usp_RegisterForSession:  zapis na sesje konferencji z autoprzydzielaniem statusu
-- Konwencja: prefiks 'usp_' (NIE 'sp_' - zarezerwowany dla procedur systemowych)

USE ConferenceDB;
GO

-- Procedura 1: usp_PurchaseTicket
-- Zakup biletu na konferencje. Walidacja okna sprzedazy, dostepnosci miejsc,
-- istnienia uczestnika i typu biletu. Cala operacja w transakcji, w razie
-- bledu pelny rollback. Generuje unikalny kod QR.
-- 
-- Parametry:
--   TicketTypeID - ID typu biletu
--   AttendeeID   - ID uczestnika
-- Zwraca:
--   TicketID     - ID utworzonego biletu

IF OBJECT_ID('usp_PurchaseTicket', 'P') IS NOT NULL
    DROP PROCEDURE usp_PurchaseTicket;
GO

CREATE PROCEDURE usp_PurchaseTicket
    @TicketTypeID INT,
    @AttendeeID   INT,
    @TicketID     INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @Today          DATE          = CAST(SYSDATETIME() AS DATE);
        DECLARE @SalesStart     DATE;
        DECLARE @SalesEnd       DATE;
        DECLARE @Price          DECIMAL(10,2);
        DECLARE @MaxQty         INT;
        DECLARE @CurrentCount   INT;
        DECLARE @TicketTypeName NVARCHAR(50);
        DECLARE @QRCode         NVARCHAR(50);

        -- Sprawdzenie czy typ biletu istnieje
        IF NOT EXISTS (SELECT 1 FROM TicketTypes WHERE TicketTypeID = @TicketTypeID)
        BEGIN
            THROW 50001, 'Typ biletu o podanym ID nie istnieje.', 1;
        END

        -- Sprawdzenie czy uczestnik istnieje
        IF NOT EXISTS (SELECT 1 FROM Attendees WHERE AttendeeID = @AttendeeID)
        BEGIN
            THROW 50002, 'Uczestnik o podanym ID nie istnieje.', 1;
        END

        -- Pobierz dane typu biletu
        SELECT
            @SalesStart     = SalesStart,
            @SalesEnd       = SalesEnd,
            @Price          = Price,
            @MaxQty         = MaxQuantity,
            @TicketTypeName = Name
        FROM TicketTypes
        WHERE TicketTypeID = @TicketTypeID;

        -- Sprawdzenie czy sprzedaz sie zaczela
        IF @Today < @SalesStart
        BEGIN
            THROW 50003, 'Sprzedaz jeszcze sie nie rozpoczela.', 1;
        END

       -- Sprawdzenie czy sprzedaz sie zakonczyla
        IF @Today > @SalesEnd
        BEGIN
            THROW 50004, 'Sprzedaz zostala zamknieta.', 1;
        END

        -- Sprawdzenie czy sa dostepne miejsca
        SELECT @CurrentCount = COUNT(*)
        FROM Tickets
        WHERE TicketTypeID = @TicketTypeID
          AND Status IN ('Active', 'Used');

        IF @CurrentCount >= @MaxQty
        BEGIN
            THROW 50005, 'Brak dostepnych biletow, osiagnieto limit sprzedazy.', 1;
        END

        -- Generowanie unikalnego kodu QR
        SET @QRCode = CONCAT('QR-T', @TicketTypeID, '-A', @AttendeeID, '-',
                             FORMAT(SYSDATETIME(), 'yyyyMMddHHmmssfff'));

        -- Wstawianie biletu
        INSERT INTO Tickets (TicketTypeID, AttendeeID, Price, Status, QRCode)
        VALUES (@TicketTypeID, @AttendeeID, @Price, 'Active', @QRCode);

        SET @TicketID = SCOPE_IDENTITY();

        COMMIT TRANSACTION;

        PRINT CONCAT('Zakup się udał: bilet ', @TicketID,
                     ' (', @TicketTypeName, ') za ', @Price, ' PLN');
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

PRINT 'Utworzono procedure usp_PurchaseTicket.';
GO

-- Procedura 2: usp_RegisterForSession
-- Zapis uczestnika na sesje. Sprawdza, czy uczestnik ma wazny bilet na
-- konferencje, czy nie jest juz zapisany, oraz pojemnosc sali. Jezeli sala
-- pelna to automatycznie przydziela status 'Waitlist', w przeciwnym razie
-- 'Confirmed'. Cala operacja w transakcji.
-- 
-- Parametry:
--   SessionID       - ID sesji
--   AttendeeID      - ID uczestnika
-- Zwraca:
--   AssignedStatus  - faktycznie przyznany status 'Confirmed' lub 'Waitlist'

IF OBJECT_ID('usp_RegisterForSession', 'P') IS NOT NULL
    DROP PROCEDURE usp_RegisterForSession;
GO

CREATE PROCEDURE usp_RegisterForSession
    @SessionID      INT,
    @AttendeeID     INT,
    @AssignedStatus NVARCHAR(20) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @ConferenceID   INT;
        DECLARE @RoomCapacity   INT;
        DECLARE @ConfirmedCount INT;
        DECLARE @SessionTitle   NVARCHAR(200);

        -- Pobiera dane sesji i sali
        SELECT
            @ConferenceID = s.ConferenceID,
            @RoomCapacity = r.Capacity,
            @SessionTitle = s.Title
        FROM Sessions s
        INNER JOIN Rooms r ON s.RoomID = r.RoomID
        WHERE s.SessionID = @SessionID;

        -- Sprawdzenie czy sesja konfrencji istnieje
        IF @ConferenceID IS NULL
        BEGIN
            THROW 50101, 'Sesja o podanym ID nie istnieje.', 1;
        END

        -- Sprawdzenie czy uczestnik istnieje
        IF NOT EXISTS (SELECT 1 FROM Attendees WHERE AttendeeID = @AttendeeID)
        BEGIN
            THROW 50102, 'Uczestnik o podanym ID nie istnieje.', 1;
        END

        -- Sprawdzenie czy uczestnik ma wazny bilet na te konferencje
        IF NOT EXISTS (
            SELECT 1
            FROM Tickets t
            INNER JOIN TicketTypes tt ON t.TicketTypeID = tt.TicketTypeID
            WHERE t.AttendeeID    = @AttendeeID
              AND tt.ConferenceID = @ConferenceID
              AND t.Status IN ('Active', 'Used')
        )
        BEGIN
            THROW 50103, 'Uczestnik nie ma waznego biletu na te konferencje.', 1;
        END

        -- Sprawdzenie czy uczestnik nie jest juz zapisany
        IF EXISTS (
            SELECT 1 FROM SessionRegistrations
            WHERE SessionID = @SessionID AND AttendeeID = @AttendeeID
        )
        BEGIN
            THROW 50104, 'Uczestnik jest juz zapisany na te sesje.', 1;
        END

        -- Sprawdzenie pojemnosci sali i przyznanie statusu
        SELECT @ConfirmedCount = COUNT(*)
        FROM SessionRegistrations
        WHERE SessionID = @SessionID
          AND Status = 'Confirmed';

        IF @ConfirmedCount >= @RoomCapacity
            SET @AssignedStatus = 'Waitlist';
        ELSE
            SET @AssignedStatus = 'Confirmed';

        -- Wstawia zapis na sesje
        INSERT INTO SessionRegistrations (SessionID, AttendeeID, Status)
        VALUES (@SessionID, @AttendeeID, @AssignedStatus);

        COMMIT TRANSACTION;

        PRINT CONCAT('Zapis się udał: uczestnik ', @AttendeeID,
                     ' na sesje "', @SessionTitle, '" jako ', @AssignedStatus);
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

PRINT 'Utworzono procedure usp_RegisterForSession';
GO
-- Projekt: ConferenceDB - System zarzadzania konferencjami
-- Opis:    Tworzy baze danych i 10 tabel z PK, FK, UQ, CHECK, DEFAULT

USE master;
GO

IF DB_ID('ConferenceDB') IS NOT NULL
BEGIN
    ALTER DATABASE ConferenceDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE ConferenceDB;
END
GO

CREATE DATABASE ConferenceDB;
GO

USE ConferenceDB;
GO

PRINT 'Baza ConferenceDB zostala utworzona';
GO

-- Tabele
-- Konferencje

CREATE TABLE Conferences (
    ConferenceID  INT            IDENTITY(1,1) NOT NULL,
    Name          NVARCHAR(150)  NOT NULL,
    StartDate     DATE           NOT NULL,
    EndDate       DATE           NOT NULL,
    Location      NVARCHAR(200)  NOT NULL,
    MaxAttendees  INT            NOT NULL,
    Status        NVARCHAR(20)   NOT NULL CONSTRAINT DF_Conferences_Status DEFAULT 'Planned',
    CONSTRAINT PK_Conferences        PRIMARY KEY (ConferenceID),
    CONSTRAINT UQ_Conferences_Name   UNIQUE (Name),
    CONSTRAINT CK_Conferences_Dates  CHECK (EndDate >= StartDate),
    CONSTRAINT CK_Conferences_MaxAtt CHECK (MaxAttendees > 0),
    CONSTRAINT CK_Conferences_Status CHECK (Status IN ('Planned','Active','Closed','Cancelled'))
);
GO

-- Sciezki tematyczne na konferencji

CREATE TABLE Tracks (
    TrackID       INT            IDENTITY(1,1) NOT NULL,
    ConferenceID  INT            NOT NULL,
    Name          NVARCHAR(100)  NOT NULL,
    Description   NVARCHAR(500)  NULL,
    CONSTRAINT PK_Tracks              PRIMARY KEY (TrackID),
    CONSTRAINT FK_Tracks_Conferences  FOREIGN KEY (ConferenceID)
                                      REFERENCES Conferences(ConferenceID)
                                      ON DELETE CASCADE,
    CONSTRAINT UQ_Tracks_NamePerConf  UNIQUE (ConferenceID, Name)
);
GO

-- Sale wykladowe

CREATE TABLE Rooms (
    RoomID        INT            IDENTITY(1,1) NOT NULL,
    Name          NVARCHAR(80)   NOT NULL,
    Capacity      INT            NOT NULL,
    Floor         INT            NOT NULL,
    HasProjector  BIT            NOT NULL CONSTRAINT DF_Rooms_HasProjector DEFAULT 1,
    CONSTRAINT PK_Rooms          PRIMARY KEY (RoomID),
    CONSTRAINT UQ_Rooms_Name     UNIQUE (Name),
    CONSTRAINT CK_Rooms_Capacity CHECK (Capacity > 0)
);
GO

-- Mowcy

CREATE TABLE Speakers (
    SpeakerID  INT            IDENTITY(1,1) NOT NULL,
    FirstName  NVARCHAR(50)   NOT NULL,
    LastName   NVARCHAR(50)   NOT NULL,
    Email      NVARCHAR(150)  NOT NULL,
    Country    NVARCHAR(50)   NULL,
    Company    NVARCHAR(100)  NULL,
    CONSTRAINT PK_Speakers       PRIMARY KEY (SpeakerID),
    CONSTRAINT UQ_Speakers_Email UNIQUE (Email),
    CONSTRAINT CK_Speakers_Email CHECK (Email LIKE '%_@_%._%')
);
GO

-- Uczestnicy

CREATE TABLE Attendees (
    AttendeeID        INT            IDENTITY(1,1) NOT NULL,
    FirstName         NVARCHAR(50)   NOT NULL,
    LastName          NVARCHAR(50)   NOT NULL,
    Email             NVARCHAR(150)  NOT NULL,
    Company           NVARCHAR(100)  NULL,
    RegistrationDate  DATETIME2      NOT NULL CONSTRAINT DF_Attendees_RegDate DEFAULT SYSDATETIME(),
    CONSTRAINT PK_Attendees       PRIMARY KEY (AttendeeID),
    CONSTRAINT UQ_Attendees_Email UNIQUE (Email),
    CONSTRAINT CK_Attendees_Email CHECK (Email LIKE '%_@_%._%')
);
GO

-- Typy biletow

CREATE TABLE TicketTypes (
    TicketTypeID  INT            IDENTITY(1,1) NOT NULL,
    ConferenceID  INT            NOT NULL,
    Name          NVARCHAR(50)   NOT NULL,
    Price         DECIMAL(10,2)  NOT NULL,
    MaxQuantity   INT            NOT NULL,
    SalesStart    DATE           NOT NULL,
    SalesEnd      DATE           NOT NULL,
    CONSTRAINT PK_TicketTypes             PRIMARY KEY (TicketTypeID),
    CONSTRAINT FK_TicketTypes_Conferences FOREIGN KEY (ConferenceID)
                                          REFERENCES Conferences(ConferenceID),
    CONSTRAINT UQ_TicketTypes_NamePerConf UNIQUE (ConferenceID, Name),
    CONSTRAINT CK_TicketTypes_Price       CHECK (Price >= 0),
    CONSTRAINT CK_TicketTypes_MaxQty      CHECK (MaxQuantity > 0),
    CONSTRAINT CK_TicketTypes_SalesDates  CHECK (SalesEnd >= SalesStart)
);
GO

-- Konkretna sesja wykladu

CREATE TABLE Sessions (
    SessionID        INT            IDENTITY(1,1) NOT NULL,
    ConferenceID     INT            NOT NULL,
    TrackID          INT            NULL,
    RoomID           INT            NOT NULL,
    SpeakerID        INT            NOT NULL,
    Title            NVARCHAR(200)  NOT NULL,
    StartTime        DATETIME2      NOT NULL,
    EndTime          DATETIME2      NOT NULL,
    SessionType      NVARCHAR(20)   NOT NULL CONSTRAINT DF_Sessions_Type  DEFAULT 'Talk',
    DifficultyLevel  NVARCHAR(20)   NOT NULL CONSTRAINT DF_Sessions_Level DEFAULT 'Intermediate',
    CONSTRAINT PK_Sessions             PRIMARY KEY (SessionID),
    CONSTRAINT FK_Sessions_Conferences FOREIGN KEY (ConferenceID) REFERENCES Conferences(ConferenceID),
    CONSTRAINT FK_Sessions_Tracks      FOREIGN KEY (TrackID)      REFERENCES Tracks(TrackID)
                                       ON DELETE SET NULL,
    CONSTRAINT FK_Sessions_Rooms       FOREIGN KEY (RoomID)       REFERENCES Rooms(RoomID),
    CONSTRAINT FK_Sessions_Speakers    FOREIGN KEY (SpeakerID)    REFERENCES Speakers(SpeakerID),
    CONSTRAINT CK_Sessions_Times       CHECK (EndTime > StartTime),
    CONSTRAINT CK_Sessions_Type        CHECK (SessionType IN ('Talk','Workshop')),
    CONSTRAINT CK_Sessions_Level       CHECK (DifficultyLevel IN ('Beginner','Intermediate','Advanced','Expert'))
);
GO

-- Bilety

CREATE TABLE Tickets (
    TicketID      INT            IDENTITY(1,1) NOT NULL,
    TicketTypeID  INT            NOT NULL,
    AttendeeID    INT            NOT NULL,
    PurchaseDate  DATETIME2      NOT NULL CONSTRAINT DF_Tickets_PurchaseDate DEFAULT SYSDATETIME(),
    Price         DECIMAL(10,2)  NOT NULL,
    Status        NVARCHAR(20)   NOT NULL CONSTRAINT DF_Tickets_Status       DEFAULT 'Active',
    QRCode        NVARCHAR(50)   NOT NULL,
    CONSTRAINT PK_Tickets             PRIMARY KEY (TicketID),
    CONSTRAINT FK_Tickets_TicketTypes FOREIGN KEY (TicketTypeID) REFERENCES TicketTypes(TicketTypeID),
    CONSTRAINT FK_Tickets_Attendees   FOREIGN KEY (AttendeeID)   REFERENCES Attendees(AttendeeID),
    CONSTRAINT UQ_Tickets_QRCode      UNIQUE (QRCode),
    CONSTRAINT CK_Tickets_Price       CHECK (Price >= 0),
    CONSTRAINT CK_Tickets_Status      CHECK (Status IN ('Active','Cancelled','Used','Refunded'))
);
GO

-- Rejestracja uczestnikow na sesje

CREATE TABLE SessionRegistrations (
    RegistrationID    INT          IDENTITY(1,1) NOT NULL,
    SessionID         INT          NOT NULL,
    AttendeeID        INT          NOT NULL,
    RegistrationDate  DATETIME2    NOT NULL CONSTRAINT DF_SessionReg_Date   DEFAULT SYSDATETIME(),
    Status            NVARCHAR(20) NOT NULL CONSTRAINT DF_SessionReg_Status DEFAULT 'Confirmed',
    CONSTRAINT PK_SessionRegistrations       PRIMARY KEY (RegistrationID),
    CONSTRAINT FK_SessionReg_Sessions        FOREIGN KEY (SessionID)  REFERENCES Sessions(SessionID)
                                             ON DELETE CASCADE,
    CONSTRAINT FK_SessionReg_Attendees       FOREIGN KEY (AttendeeID) REFERENCES Attendees(AttendeeID),
    CONSTRAINT UQ_SessionReg_SessionAttendee UNIQUE (SessionID, AttendeeID),
    CONSTRAINT CK_SessionReg_Status          CHECK (Status IN ('Confirmed','Waitlist','Cancelled','Attended'))
);
GO

-- Oddzielna tabela z historia cen (uzupelniana przez trigger) 

CREATE TABLE PriceHistory (
    HistoryID     INT            IDENTITY(1,1) NOT NULL,
    TicketTypeID  INT            NOT NULL,
    OldPrice      DECIMAL(10,2)  NOT NULL,
    NewPrice      DECIMAL(10,2)  NOT NULL,
    ChangedAt     DATETIME2      NOT NULL CONSTRAINT DF_PriceHistory_ChangedAt DEFAULT SYSDATETIME(),
    ChangedBy     NVARCHAR(100)  NOT NULL CONSTRAINT DF_PriceHistory_ChangedBy DEFAULT SUSER_SNAME(),
    CONSTRAINT PK_PriceHistory             PRIMARY KEY (HistoryID),
    CONSTRAINT FK_PriceHistory_TicketTypes FOREIGN KEY (TicketTypeID) REFERENCES TicketTypes(TicketTypeID),
    CONSTRAINT CK_PriceHistory_Prices      CHECK (OldPrice >= 0 AND NewPrice >= 0)
);
GO

PRINT 'Utworzono 10 tabel zawierajacych PK, FK, UQ, CHECK, DEFAULT';
GO

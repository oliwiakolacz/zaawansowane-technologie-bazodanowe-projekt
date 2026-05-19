-- Projekt: ConferenceDB - System zarzadzania konferencjami
-- Opis:    Wstawia przykladowe dane do wszystkich 10 tabel

USE ConferenceDB;
GO

SET NOCOUNT ON;
GO

-- Konfernecje  (IT, medycyna, marketing)

INSERT INTO Conferences (Name, StartDate, EndDate, Location, MaxAttendees, Status) VALUES
(N'DevOps Days Warsaw 2025',                              '2025-09-15', '2025-09-16', N'Warszawa, PL',  800,   N'Closed'),
(N'Kube Europe 2025',                                     '2025-03-19', '2025-03-22', N'Berlin, DE',    12000, N'Closed'),
(N'Python PL 2025',                                       '2025-08-15', '2025-08-17', N'Lublin, PL',    600,   N'Closed'),
(N'Polish Cloud Conference 2025',                         '2025-10-10', '2025-10-11', N'Warszawa, PL',  1500,  N'Closed'),
(N'Kongres Polskiego Towarzystwa Kardiologicznego 2025',  '2025-09-19', '2025-09-21', N'Katowice, PL',  4500,  N'Closed'),
(N'Security 2025',                                        '2025-04-05', '2025-04-06', N'Warszawa, PL',  400,   N'Closed'),
(N'Marketing Week Warsaw 2025',                           '2025-06-03', '2025-06-05', N'Warszawa, PL',  1200,  N'Closed'),
(N'Hackaton 2025',                                        '2025-12-09', '2025-12-12', N'Londyn, UK',    8000,  N'Active'),
(N'Data Science Summit 2025',                             '2025-11-28', '2025-11-29', N'Warszawa, PL',  1000,  N'Cancelled'),
(N'DevOps Days Warsaw 2026',                              '2026-09-14', '2026-09-15', N'Warszawa, PL',  1000,  N'Planned');
GO

-- Sciezki tematyczne na konferencji

INSERT INTO Tracks (ConferenceID, Name, Description) VALUES
(1, N'DevOps',               N'AWS DevOps'),
(1, N'Security',             N'Bezpieczeństwo aplikacji i infrastruktury'),
(1, N'Cloud Native',         N'Konteneryzacja i orchestracja'),
(2, N'Kubernetes',           N'Kubernetes core i networking'),
(2, N'Observability',        N'Tracing, metrics, logging'),
(3, N'Web Development',      N'Frameworki webowe w Pythonie'),
(3, N'Data Science',         N'Pandas, numpy, ML'),
(4, N'Cloud Architecture',   N'AWS, Azure, GCP'),
(5, N'Diagnostyka',          N'Badania obrazowe'),
(5, N'Interwencja',          N'Kardiologia kliniczna'),
(10, N'Platform Engineering', N'Infrastructure as code, GitOps, IDP');
GO

-- Sale wykladowe

INSERT INTO Rooms (Name, Capacity, Floor, HasProjector) VALUES
(N'Sala Główna',          300, 0, 1),
(N'Sala A',               100, 1, 1),
(N'Sala B',                80, 1, 1),
(N'Sala C',                40, 2, 1),
(N'Sala D',                30, 2, 0),
(N'Workshop Lab',          10, 2, 1),
(N'Audytorium I',         250, 0, 1),
(N'Audytorium II',        150, 0, 1),
(N'Hall Berlin',          500, 0, 1),
(N'Sala VIP',              50, 3, 1),
(N'Sala Komputerowa',      35, 2, 1),
(N'Sala Konferencyjna',    60, 1, 1);
GO

-- Mowcy

INSERT INTO Speakers (FirstName, LastName, Email, Country, Company) VALUES
(N'Tomasz',    N'Kowalski',     N'tomasz.kowalski@allegro.pl',    N'Polska',    N'Allegro'),
(N'Anna',      N'Nowak',        N'anna.nowak@cdpr.pl',            N'Polska',    N'CD Projekt Red'),
(N'Piotr',     N'Wiśniewski',   N'piotr.wisniewski@comarch.com',  N'Polska',    N'Comarch'),
(N'Maria',     N'Wójcik',       N'maria.wojcik@cmkp.edu.pl',      N'Polska',    N'CMKP'),
(N'Jan',       N'Kowalczyk',    N'jan.kowalczyk@asseco.com',      N'Polska',    N'Asseco'),
(N'Katarzyna', N'Lewandowska',  N'k.lewandowska@umed.lodz.pl',    N'Polska',    N'Uniwersytet Medyczny Łódź'),
(N'John',      N'Smith',        N'john.smith@google.com',         N'USA',       N'Google'),
(N'Sarah',     N'Johnson',      N'sarah.j@bbc.co.uk',             N'UK',        N'BBC'),
(N'Hans',      N'Mueller',      N'hans.mueller@sap.com',          N'Niemcy',    N'SAP'),
(N'Pieter',    N'de Vries',     N'p.devries@ing.nl',              N'Holandia',  N'ING'),
(N'Lisa',      N'Anderson',     N'lisa.anderson@microsoft.com',   N'USA',       N'Microsoft'),
(N'David',     N'Brown',        N'david.brown@github.com',        N'UK',        N'GitHub');
GO

-- Uczestnicy

INSERT INTO Attendees (FirstName, LastName, Email, Company) VALUES
(N'Krzysztof', N'Nowak',         N'krzysztof.nowak@gmail.com',     N'Asseco'),
(N'Magdalena', N'Kowalska',      N'magdalena.k@wp.pl',             NULL),
(N'Adam',      N'Mazur',         N'adam.mazur@allegro.pl',         N'Allegro'),
(N'Ewa',       N'Kowalik',       N'ewa.kowalik@interia.pl',        N'IBM'),
(N'Marek',     N'Pawlak',        N'marek.pawlak@onet.pl',          N'Comarch'),
(N'Joanna',    N'Wiśniewska',    N'j.wisniewska@gmail.com',        N'Asseco'),
(N'Tomasz',    N'Adamski',       N'tomasz.adamski@op.pl',          NULL),
(N'Łukasz',    N'Brzozowski',    N'lukasz.brzozowski@google.com',  N'Google'),
(N'Michael',   N'Brown',         N'm.brown@gmail.com',             N'Tesla'),
(N'Emily',     N'Davis',         N'emily.davis@hotmail.com',       N'Spotify'),
(N'Klaus',     N'Schmidt',       N'k.schmidt@web.de',              N'BMW'),
(N'Maria',     N'Garcia',        N'm.garcia@gmail.com',            N'Telefonica'),
(N'Yuki',      N'Sato',          N'yuki.sato@yahoo.co.jp',         N'Sony'),
(N'Robert',    N'Chen',          N'robert.chen@gmail.com',         N'Apple'),
(N'Sven',      N'Olsen',         N'sven.olsen@gmail.com',          N'Spotify');
GO

-- Typy biletow

INSERT INTO TicketTypes (ConferenceID, Name, Price, MaxQuantity, SalesStart, SalesEnd) VALUES
(1, N'Early Bird',  299.00, 200,  '2025-04-01', '2025-06-30'),
(1, N'Standard',    499.00, 500,  '2025-07-01', '2025-09-14'),
(1, N'Student',      99.00, 100,  '2025-04-01', '2025-09-14'),
(2, N'Early Bird',  599.00, 3000, '2023-12-01', '2025-01-31'),
(2, N'Standard',    899.00, 8000, '2025-02-01', '2025-03-18'),
(3, N'Standard',    199.00, 400,  '2025-05-01', '2025-08-14'),
(3, N'Student',      89.00, 200,  '2025-05-01', '2025-08-14'),
(4, N'Early Bird',  399.00, 500,  '2025-07-01', '2025-08-31'), 
(4, N'Standard',    599.00, 1000, '2025-09-01', '2025-10-09'),
(5, N'Standard',    450.00, 4000, '2025-04-01', '2025-09-18'),
(7, N'Standard',    799.00, 1000, '2025-02-01', '2025-06-02'), 
(7, N'VIP',        1499.00, 200,  '2025-02-01', '2025-06-02'),
(10, N'Standard',   599.00, 500,  '2026-05-01', '2026-09-13');
GO

-- Konkretna sesja wykladu

INSERT INTO Sessions (ConferenceID, TrackID, RoomID, SpeakerID, Title, StartTime, EndTime, SessionType, DifficultyLevel) VALUES
(1, NULL, 1,  1, N'Future of DevOps',                    '2025-09-15 09:00:00', '2025-09-15 10:00:00', N'Talk',      N'Beginner'),
(1, 1,    6,  2, N'Git w Kubernetes - praktyczny warsztat',  '2025-09-15 14:00:00', '2025-09-15 16:00:00', N'Workshop',  N'Intermediate'),
(1, 2,    2,  7, N'Sec Architecture',                      '2025-09-15 11:00:00', '2025-09-15 12:00:00', N'Talk',      N'Advanced'),
(1, 3,    2,  9, N'Services w produkcji',                   '2025-09-16 10:00:00', '2025-09-16 11:00:00', N'Talk',      N'Advanced'),
(2, 4,    9, 11, N'Kubernetes 1.30: What is New',               '2025-03-19 09:00:00', '2025-03-19 10:00:00', N'Talk',      N'Beginner'),
(2, 5,    8,  8, N'OpenTelemetry Best Practices',               '2025-03-20 14:00:00', '2025-03-20 15:00:00', N'Talk',      N'Intermediate'),
(3, 6,    3,  3, N'Python 3.12',                  '2025-08-15 14:00:00', '2025-08-15 15:00:00', N'Talk',      N'Intermediate'),
(3, 7,    4,  2, N'Pandas 2.0',                      '2025-08-16 11:00:00', '2025-08-16 12:00:00', N'Talk',      N'Intermediate'),
(3, NULL, 3,  5, N'Python tricks',            '2025-08-17 16:00:00', '2025-08-17 17:00:00', N'Talk',      N'Beginner'),
(4, 8,    2,  1, N'Multi-Cloud',                 '2025-10-10 10:00:00', '2025-10-10 11:00:00', N'Talk',      N'Advanced'),
(4, 8,    2, 12, N'AWS vs Azure',                  '2025-10-11 14:00:00', '2025-10-11 15:00:00', N'Talk',      N'Intermediate'),
(5, 9,   7,  4, N'Echokardiografia - co nowego',            '2025-09-19 10:00:00', '2025-09-19 11:00:00', N'Talk',      N'Intermediate'),
(5, 10,   8,  6, N'Przyszłe procedury medyczne', '2025-09-20 11:00:00', '2025-09-20 12:00:00', N'Talk',      N'Advanced'),
(10, 11,  2, 11, N'Platform jako produkt - lessons learned', '2026-09-14 10:00:00', '2026-09-14 11:00:00', N'Talk', N'Intermediate');
GO

-- Bilety

INSERT INTO Tickets (TicketTypeID, AttendeeID, PurchaseDate, Price, Status, QRCode) VALUES
(1,  1, '2025-05-15 10:23:00', 299.00, N'Used',     N'QR-DDW2025-001'),
(2,  3, '2025-08-02 14:11:00', 499.00, N'Used',     N'QR-DDW2025-002'),
(2,  5, '2025-08-15 09:45:00', 499.00, N'Used',     N'QR-DDW2025-003'),
(2,  6, '2025-08-20 16:30:00', 499.00, N'Used',     N'QR-DDW2025-004'),
(1,  8, '2025-06-01 11:00:00', 299.00, N'Used',     N'QR-DDW2025-005'),
(3,  7, '2025-07-10 13:22:00',  99.00, N'Used',     N'QR-DDW2025-006'),
(2, 10, '2025-09-01 17:45:00', 499.00, N'Cancelled',N'QR-DDW2025-007'),
(2, 11, '2025-09-10 10:00:00', 499.00, N'Used',     N'QR-DDW2025-008'),
(2, 15, '2025-09-12 14:00:00', 499.00, N'Active',   N'QR-DDW2025-009'),
(4,  9, '2025-01-15 12:00:00', 599.00, N'Used',     N'QR-KC2025-001'),
(5, 12, '2025-02-15 14:30:00', 899.00, N'Used',     N'QR-KC2025-002'),
(5, 13, '2025-03-01 09:00:00', 899.00, N'Used',     N'QR-KC2025-003'),
(4, 14, '2025-01-20 11:11:00', 599.00, N'Refunded', N'QR-KC2025-004'),
(6,  2, '2025-06-01 10:00:00', 199.00, N'Used',     N'QR-PYC2025-001'),
(7,  4, '2025-06-15 15:30:00',  89.00, N'Used',     N'QR-PYC2025-002'),
(6, 15, '2025-07-01 09:00:00', 199.00, N'Used',     N'QR-PYC2025-003'),
(8,  1, '2025-08-15 13:00:00', 399.00, N'Used',     N'QR-PCC2025-001'),
(9,  3, '2025-09-20 16:00:00', 599.00, N'Active',   N'QR-PCC2025-002'),
(10, 4, '2025-08-01 10:00:00', 450.00, N'Used',     N'QR-PTK2025-001');
GO

-- Rejestracja uczestnikow na sesje

INSERT INTO SessionRegistrations (SessionID, AttendeeID, RegistrationDate, Status) VALUES
(1,  1, '2025-09-10 08:00:00', N'Attended'),
(1,  3, '2025-09-10 09:15:00', N'Attended'),
(1,  5, '2025-09-11 14:30:00', N'Attended'),
(1,  6, '2025-09-11 15:00:00', N'Attended'),
(1,  8, '2025-09-12 10:00:00', N'Attended'),
(2,  1, '2025-09-10 08:01:00', N'Confirmed'),
(2,  3, '2025-09-10 09:16:00', N'Confirmed'),
(2,  5, '2025-09-11 14:31:00', N'Confirmed'),
(2,  6, '2025-09-11 15:01:00', N'Confirmed'),
(2,  8, '2025-09-12 10:01:00', N'Confirmed'),
(2, 11, '2025-09-13 09:00:00', N'Confirmed'),
(2,  7, '2025-09-13 10:00:00', N'Confirmed'),
(2, 10, '2025-09-13 11:00:00', N'Cancelled'),
(3,  1, '2025-09-10 08:02:00', N'Attended'),
(3,  6, '2025-09-11 15:02:00', N'Attended'),
(3, 11, '2025-09-13 09:01:00', N'Attended'),
(4,  3, '2025-09-10 09:18:00', N'Attended'),
(4,  5, '2025-09-11 14:33:00', N'Attended'),
(5,  9, '2025-03-15 10:00:00', N'Attended'),
(5, 12, '2025-03-16 11:00:00', N'Attended'),
(7,  2, '2025-08-10 12:00:00', N'Attended'),
(7, 15, '2025-08-12 14:00:00', N'Attended'),
(9,  4, '2025-08-12 16:30:00', N'Attended'),
(9,  2, '2025-08-13 10:00:00', N'Confirmed'),
(9, 15, '2025-08-14 11:00:00', N'Waitlist'),
(12,  4, '2025-09-15 10:00:00', N'Attended'),
(12,  6, '2025-09-15 11:00:00', N'Attended');
GO

-- Oddzielna tabela z historia cen (uzupelniana przez trigger) 

INSERT INTO PriceHistory (TicketTypeID, OldPrice, NewPrice, ChangedAt, ChangedBy) VALUES
( 1, 199.00, 249.00, '2025-04-01 00:00:00', N'admin@conferencedb.local'),
( 1, 249.00, 299.00, '2025-05-15 00:00:00', N'admin@conferencedb.local'),
( 2, 449.00, 499.00, '2025-07-15 00:00:00', N'admin@conferencedb.local'),
( 3,  79.00,  99.00, '2025-06-01 00:00:00', N'admin@conferencedb.local'),
( 4, 499.00, 549.00, '2023-12-15 00:00:00', N'kubecon-eu@cncf.io'),
( 4, 549.00, 599.00, '2025-01-15 00:00:00', N'kubecon-eu@cncf.io'),
( 5, 799.00, 899.00, '2025-02-15 00:00:00', N'kubecon-eu@cncf.io'),
( 8, 349.00, 399.00, '2025-08-01 00:00:00', N'admin@pccloud.pl'),
(11, 699.00, 799.00, '2025-04-15 00:00:00', N'admin@marketingweek.pl'),
(12,1299.00,1499.00, '2025-04-15 00:00:00', N'admin@marketingweek.pl');
GO

PRINT 'Dodano wszystkie rekordy poprawnie';
GO

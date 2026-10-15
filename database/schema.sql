
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
   client_id INTEGER PRIMARY KEY AUTOINCREMENT,
   full_name TEXT NOT NULL,
   phone TEXT NOT NULL UNIQUE,
   email TEXT
);

CREATE TABLE IF NOT EXISTS tours (
 tour_id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 destination TEXT NOT NULL,
 price REAL NOT NULL CHECK (price >= 0),
    available INTEGER NOT NULL DEFAULT 1
    CHECK (available IN (0, 1))
    );

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Новая'
    CHECK (status IN (
    'Новая',
    'Забронирована',
    'Отменена'
)),
    FOREIGN KEY (client_id)
    REFERENCES clients(client_id),
    FOREIGN KEY (tour_id)
    REFERENCES tours(tour_id)
    );

INSERT OR IGNORE INTO clients
    (client_id, full_name, phone, email)
VALUES
    (1, 'Иванов Иван Иванович', '+79990000001', 'ivanov@example.com'),
    (2, 'Мурсков Роман Сергеевич', '+79990000002', 'murskov@example.com'),
    (3, 'Шеронов Федор Алексеевич', '+79990000003', 'sheronov@example.com');

INSERT OR IGNORE INTO tours
    (tour_id, title, destination, price, available)
VALUES
    (1, 'Отдых на море', 'Сочи', 45000, 1),
    (2, 'Горный отдых', 'Ереван', 60000, 1),
    (3, 'Знакомство с культурой', 'Тель-Авив', 35000, 0);

INSERT OR IGNORE INTO bookings
    (booking_id, client_id, tour_id, booking_date, status)
VALUES
    (1, 1, 1, '2026-10-10', 'Забронирована'),
    (2, 2, 2, '2026-10-11', 'Новая'),
    (3, 3, 3, '2026-10-12', 'Отменена');

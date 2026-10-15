print('Hello, World!')
print('My name is Roman!')

# tytytytytytyty
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent

DB_PATH = PROJECT_DIR / "tourism.db"


SCHEMA_PATH = PROJECT_DIR / "database" / "schema.sql"


def main():

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute("PRAGMA foreign_keys = ON")


        schema = SCHEMA_PATH.read_text(encoding="utf-8")


        connection.executescript(schema)


        cursor = connection.cursor()

        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()

        cursor.execute("SELECT * FROM tours")
        tours = cursor.fetchall()

        cursor.execute("""
                       SELECT
                           bookings.booking_id,
                           clients.full_name,
                           tours.title,
                           bookings.booking_date,
                           bookings.status
                       FROM bookings
                                JOIN clients
                                     ON bookings.client_id = clients.client_id
                                JOIN tours
                                     ON bookings.tour_id = tours.tour_id
                       """)
        bookings = cursor.fetchall()

        print("База данных успешно создана!")
        print("\nКлиенты:")
        for client in clients:
            print(client)

        print("\nТуры:")
        for tour in tours:
            print(tour)

        print("\nЗаявки:")
        for booking in bookings:
            print(booking)


if __name__ == "__main__":
    main()

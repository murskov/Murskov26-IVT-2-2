from datetime import date
from tourism.database import get_connection
from tourism.models import Booking

class BookingRepository:
    STATUSES = ("Новая", "Забронирована", "Отменена")

    @staticmethod
    def _model(row):
        return Booking(row["booking_id"], row["client_id"], row["tour_id"], row["booking_date"], row["status"], row["manager_id"]) if row else None

    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM bookings ORDER BY booking_id").fetchall()
        return [self._model(row) for row in rows]

    def get_by_id(self, booking_id):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM bookings WHERE booking_id=?", (booking_id,)).fetchone())

    def get_by_client(self, client_id):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM bookings WHERE client_id=? ORDER BY booking_id", (client_id,)).fetchall()
        return [self._model(row) for row in rows]

    def create(self, client_id, tour_id, manager_id=None, status="Новая"):
        with get_connection() as db:
            cursor = db.execute("INSERT INTO bookings(client_id,tour_id,booking_date,status,manager_id) VALUES(?,?,?,?,?)", (client_id, tour_id, date.today().isoformat(), status, manager_id))
            return cursor.lastrowid

    def update_status(self, booking_id, status):
        if status not in self.STATUSES:
            raise ValueError("Недопустимый статус заявки")
        with get_connection() as db:
            cursor = db.execute("UPDATE bookings SET status=? WHERE booking_id=?", (status, booking_id))
            return cursor.rowcount > 0

    def assign_manager(self, booking_id, manager_id):
        with get_connection() as db:
            cursor = db.execute("UPDATE bookings SET manager_id=? WHERE booking_id=?", (manager_id, booking_id))
            return cursor.rowcount > 0

    def delete(self, booking_id):
        with get_connection() as db:
            cursor = db.execute("DELETE FROM bookings WHERE booking_id=?", (booking_id,))
            return cursor.rowcount > 0
    def pay_booking(self, client_id, tour_id, price, booking_date):
        """Атомарно списывает деньги клиента и создаёт оплаченную заявку."""
        with get_connection() as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute("UPDATE clients SET balance=balance-? WHERE client_id=? AND balance>=?", (price, client_id, price))
            if cursor.rowcount == 0:
                raise ValueError("Недостаточно средств или клиент не найден")
            booking = db.execute("INSERT INTO bookings(client_id,tour_id,booking_date,status,manager_id) VALUES(?,?,?,'Забронирована',NULL)", (client_id, tour_id, booking_date))
            return booking.lastrowid

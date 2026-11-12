from tourism.database import get_connection
from tourism.models import Tour

class TourRepository:
    @staticmethod
    def _model(row):
        return Tour(row["tour_id"], row["title"], row["destination"], row["price"], row["available"]) if row else None

    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM tours ORDER BY tour_id").fetchall()
        return [self._model(row) for row in rows]

    def get_by_id(self, tour_id):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM tours WHERE tour_id=?", (tour_id,)).fetchone())

    def create(self, title, destination, price, available=1):
        with get_connection() as db:
            cursor = db.execute("INSERT INTO tours(title,destination,price,available) VALUES(?,?,?,?)", (title, destination, price, available))
            return cursor.lastrowid

    def update(self, tour_id, title, destination, price, available):
        with get_connection() as db:
            cursor = db.execute("UPDATE tours SET title=?,destination=?,price=?,available=? WHERE tour_id=?", (title, destination, price, available, tour_id))
            return cursor.rowcount > 0

    def set_availability(self, tour_id, available):
        with get_connection() as db:
            cursor = db.execute("UPDATE tours SET available=? WHERE tour_id=?", (available, tour_id))
            return cursor.rowcount > 0

    def delete(self, tour_id):
        with get_connection() as db:
            cursor = db.execute("DELETE FROM tours WHERE tour_id=?", (tour_id,))
            return cursor.rowcount > 0

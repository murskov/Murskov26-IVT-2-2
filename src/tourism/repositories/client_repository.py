from tourism.database import get_connection
from tourism.models import Client

class ClientRepository:
    @staticmethod
    def _model(row):
        return Client(row["client_id"], row["full_name"], row["phone"], row["email"], row["login"], row["password_hash"], row["balance"]) if row else None

    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM clients ORDER BY client_id").fetchall()
        return [self._model(row) for row in rows]

    def get_by_id(self, client_id):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM clients WHERE client_id=?", (client_id,)).fetchone())

    def get_by_login(self, login):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM clients WHERE login=?", (login,)).fetchone())

    def get_by_phone(self, phone):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM clients WHERE phone=?", (phone,)).fetchone())

    def create(self, full_name, phone, email=None, login=None, password_hash=None):
        with get_connection() as db:
            cursor = db.execute("INSERT INTO clients(full_name,phone,email,login,password_hash) VALUES(?,?,?,?,?)", (full_name, phone, email or None, login, password_hash))
            return cursor.lastrowid

    def update(self, client_id, full_name, phone, email):
        with get_connection() as db:
            cursor = db.execute("UPDATE clients SET full_name=?,phone=?,email=? WHERE client_id=?", (full_name, phone, email or None, client_id))
            return cursor.rowcount > 0

    def delete(self, client_id):
        with get_connection() as db:
            cursor = db.execute("DELETE FROM clients WHERE client_id=?", (client_id,))
            return cursor.rowcount > 0

    def change_balance(self, client_id, amount):
        with get_connection() as db:
            cursor = db.execute("UPDATE clients SET balance=balance+? WHERE client_id=? AND balance+?>=0", (amount, client_id, amount))
            return cursor.rowcount > 0

from tourism.database import get_connection
from tourism.models import Administrator

class AdministratorRepository:
    @staticmethod
    def _model(row):
        return Administrator(row["admin_id"], row["full_name"], row["login"], row["password_hash"]) if row else None

    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM administrators ORDER BY admin_id").fetchall()
        return [self._model(row) for row in rows]

    def get_by_id(self, admin_id):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM administrators WHERE admin_id=?", (admin_id,)).fetchone())

    def get_by_login(self, login):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM administrators WHERE login=?", (login,)).fetchone())

    def create(self, full_name, login, password_hash):
        with get_connection() as db:
            cursor = db.execute("INSERT INTO administrators(full_name,login,password_hash) VALUES(?,?,?)", (full_name, login, password_hash))
            return cursor.lastrowid

from tourism.database import get_connection
from tourism.models import Manager

class ManagerRepository:
    @staticmethod
    def _model(row):
        return Manager(row["manager_id"], row["full_name"], row["login"], row["password_hash"]) if row else None

    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM managers ORDER BY manager_id").fetchall()
        return [self._model(row) for row in rows]

    def get_by_id(self, manager_id):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM managers WHERE manager_id=?", (manager_id,)).fetchone())

    def get_by_login(self, login):
        with get_connection() as db:
            return self._model(db.execute("SELECT * FROM managers WHERE login=?", (login,)).fetchone())

    def create(self, full_name, login, password_hash):
        with get_connection() as db:
            cursor = db.execute("INSERT INTO managers(full_name,login,password_hash) VALUES(?,?,?)", (full_name, login, password_hash))
            return cursor.lastrowid

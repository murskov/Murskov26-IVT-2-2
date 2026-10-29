
from dataclasses import dataclass
from pathlib import Path
import hashlib
import hmac
import os
import sqlite3
from datetime import date

# Пути: файл лежит в src/tourism, а база и папка database — в корне проекта.
PROJECT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_DIR / "tourism.db"
SCHEMA_PATH = PROJECT_DIR / "database" / "schema.sql"

# ============================ МОДЕЛИ ДАННЫХ ============================
@dataclass
class Client:
    client_id: int
    full_name: str
    phone: str
    email: str | None = None
    login: str | None = None
    password_hash: str | None = None
    balance: float = 0.0

@dataclass
class Tour:
    tour_id: int
    title: str
    destination: str
    price: float
    available: int

@dataclass
class Booking:
    booking_id: int
    client_id: int
    tour_id: int
    booking_date: str
    status: str
    manager_id: int | None = None

@dataclass
class Manager:
    manager_id: int
    full_name: str
    login: str
    password_hash: str

@dataclass
class Administrator:
    admin_id: int
    full_name: str
    login: str
    password_hash: str

# ============================ ДОСТУП К БД =============================
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Не найден SQL-файл: {SCHEMA_PATH}")
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # Мягкая миграция: сохраняет существующие данные из старой tourism.db.
        columns = {row[1] for row in connection.execute("PRAGMA table_info(clients)")}
        if "login" not in columns:
            connection.execute("ALTER TABLE clients ADD COLUMN login TEXT")
        if "password_hash" not in columns:
            connection.execute("ALTER TABLE clients ADD COLUMN password_hash TEXT")
        if "balance" not in columns:
            connection.execute("ALTER TABLE clients ADD COLUMN balance REAL NOT NULL DEFAULT 0")
        booking_columns = {row[1] for row in connection.execute("PRAGMA table_info(bookings)")}
        if "manager_id" not in booking_columns:
            connection.execute("ALTER TABLE bookings ADD COLUMN manager_id INTEGER REFERENCES managers(manager_id)")

# ================================ МОДЕЛЬ ===============================
def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt.hex() + ":" + digest.hex()


def _check_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 200_000)
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False

# ============================ РЕПОЗИТОРИИ =============================
class ClientRepository:
    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM clients ORDER BY client_id").fetchall()
        return [Client(r["client_id"], r["full_name"], r["phone"], r["email"], r["login"], r["password_hash"], r["balance"]) for r in rows]

    def get_by_id(self, client_id):
        with get_connection() as db:
            r = db.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,)).fetchone()
        return Client(r["client_id"], r["full_name"], r["phone"], r["email"], r["login"], r["password_hash"], r["balance"]) if r else None

    def get_by_login(self, login):
        with get_connection() as db:
            r = db.execute("SELECT * FROM clients WHERE login = ?", (login,)).fetchone()
        return Client(r["client_id"], r["full_name"], r["phone"], r["email"], r["login"], r["password_hash"], r["balance"]) if r else None

    def create(self, full_name, phone, email=None, login=None, password_hash=None):
        with get_connection() as db:
            cur = db.execute("INSERT INTO clients(full_name, phone, email, login, password_hash) VALUES (?, ?, ?, ?, ?)",
                             (full_name, phone, email or None, login, password_hash))
            return cur.lastrowid

    def update(self, client_id, full_name, phone, email):
        with get_connection() as db:
            cur = db.execute("UPDATE clients SET full_name=?, phone=?, email=? WHERE client_id=?",
                             (full_name, phone, email or None, client_id))
            return cur.rowcount > 0

    def delete(self, client_id):
        with get_connection() as db:
            cur = db.execute("DELETE FROM clients WHERE client_id=?", (client_id,))
            return cur.rowcount > 0

    def change_balance(self, client_id, amount):
        with get_connection() as db:
            cur = db.execute("UPDATE clients SET balance=balance+? WHERE client_id=? AND balance+? >= 0",
                             (amount, client_id, amount))
            return cur.rowcount > 0

class TourRepository:
    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM tours ORDER BY tour_id").fetchall()
        return [Tour(r["tour_id"], r["title"], r["destination"], r["price"], r["available"]) for r in rows]

    def get_by_id(self, tour_id):
        with get_connection() as db:
            r = db.execute("SELECT * FROM tours WHERE tour_id=?", (tour_id,)).fetchone()
        return Tour(r["tour_id"], r["title"], r["destination"], r["price"], r["available"]) if r else None

    def create(self, title, destination, price, available=1):
        with get_connection() as db:
            cur = db.execute("INSERT INTO tours(title,destination,price,available) VALUES(?,?,?,?)",
                             (title, destination, price, available))
            return cur.lastrowid

    def update(self, tour_id, title, destination, price, available):
        with get_connection() as db:
            cur = db.execute("UPDATE tours SET title=?, destination=?, price=?, available=? WHERE tour_id=?",
                             (title, destination, price, available, tour_id))
            return cur.rowcount > 0

    def delete(self, tour_id):
        with get_connection() as db:
            cur = db.execute("DELETE FROM tours WHERE tour_id=?", (tour_id,))
            return cur.rowcount > 0

class BookingRepository:
    def get_all(self):
        with get_connection() as db:
            return db.execute("""SELECT b.booking_id, c.full_name, t.title, b.booking_date,
                                      b.status, b.manager_id, b.client_id, b.tour_id
                               FROM bookings b JOIN clients c ON c.client_id=b.client_id
                               JOIN tours t ON t.tour_id=b.tour_id ORDER BY b.booking_id""").fetchall()

    def get_by_id(self, booking_id):
        with get_connection() as db:
            r = db.execute("SELECT * FROM bookings WHERE booking_id=?", (booking_id,)).fetchone()
        return Booking(r["booking_id"], r["client_id"], r["tour_id"], r["booking_date"], r["status"], r["manager_id"]) if r else None

    def create(self, client_id, tour_id, manager_id=None):
        with get_connection() as db:
            cur = db.execute("INSERT INTO bookings(client_id,tour_id,booking_date,status,manager_id) VALUES(?,?,?,'Новая',?)",
                             (client_id, tour_id, date.today().isoformat(), manager_id))
            return cur.lastrowid

    def update_status(self, booking_id, status):
        if status not in ("Новая", "Забронирована", "Отменена"):
            raise ValueError("Недопустимый статус заявки")
        with get_connection() as db:
            cur = db.execute("UPDATE bookings SET status=? WHERE booking_id=?", (status, booking_id))
            return cur.rowcount > 0

    def assign_manager(self, booking_id, manager_id):
        with get_connection() as db:
            cur = db.execute("UPDATE bookings SET manager_id=? WHERE booking_id=?", (manager_id, booking_id))
            return cur.rowcount > 0

    def delete(self, booking_id):
        with get_connection() as db:
            cur = db.execute("DELETE FROM bookings WHERE booking_id=?", (booking_id,))
            return cur.rowcount > 0

class ManagerRepository:
    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM managers ORDER BY manager_id").fetchall()
        return [Manager(r["manager_id"], r["full_name"], r["login"], r["password_hash"]) for r in rows]

    def get_by_login(self, login):
        with get_connection() as db:
            r = db.execute("SELECT * FROM managers WHERE login=?", (login,)).fetchone()
        return Manager(r["manager_id"], r["full_name"], r["login"], r["password_hash"]) if r else None

    def create(self, full_name, login, password_hash):
        with get_connection() as db:
            cur = db.execute("INSERT INTO managers(full_name,login,password_hash) VALUES(?,?,?)", (full_name, login, password_hash))
            return cur.lastrowid

class AdministratorRepository:
    def get_by_login(self, login):
        with get_connection() as db:
            r = db.execute("SELECT * FROM administrators WHERE login=?", (login,)).fetchone()
        return Administrator(r["admin_id"], r["full_name"], r["login"], r["password_hash"]) if r else None

    def get_all(self):
        with get_connection() as db:
            rows = db.execute("SELECT * FROM administrators ORDER BY admin_id").fetchall()
        return [Administrator(r["admin_id"], r["full_name"], r["login"], r["password_hash"]) for r in rows]

    def create(self, full_name, login, password_hash):
        with get_connection() as db:
            cur = db.execute("INSERT INTO administrators(full_name,login,password_hash) VALUES(?,?,?)", (full_name, login, password_hash))
            return cur.lastrowid

clients = ClientRepository()
tours = TourRepository()
bookings = BookingRepository()
managers = ManagerRepository()
administrators = AdministratorRepository()

# ============================ СЕРВИСЫ =================================
class AuthService:
    def register_client(self, full_name, phone, email, login, password):
        if not full_name.strip() or not phone.strip() or not login.strip() or len(password) < 6:
            raise ValueError("Заполните имя, телефон и логин; пароль должен быть не короче 6 символов")
        if clients.get_by_login(login) or managers.get_by_login(login) or administrators.get_by_login(login):
            raise ValueError("Такой логин уже занят")
        if any(c.phone == phone for c in clients.get_all()):
            raise ValueError("Клиент с таким телефоном уже существует")
        return clients.create(full_name.strip(), phone.strip(), email.strip(), login.strip(), _hash_password(password))

    def login(self, login, password):
        client = clients.get_by_login(login)
        if client and client.password_hash and _check_password(password, client.password_hash):
            return ("Клиент", client)
        manager = managers.get_by_login(login)
        if manager and _check_password(password, manager.password_hash):
            return ("Менеджер", manager)
        admin = administrators.get_by_login(login)
        if admin and _check_password(password, admin.password_hash):
            return ("Администратор", admin)
        return None

    def create_first_admin(self, full_name, login, password):
        if administrators.get_all():
            raise ValueError("Администратор уже существует")
        if not full_name.strip() or not login.strip() or len(password) < 6:
            raise ValueError("Имя и логин обязательны, пароль — минимум 6 символов")
        if clients.get_by_login(login) or managers.get_by_login(login):
            raise ValueError("Такой логин уже занят")
        return administrators.create(full_name.strip(), login.strip(), _hash_password(password))

    def create_manager(self, full_name, login, password):
        if not full_name.strip() or not login.strip() or len(password) < 6:
            raise ValueError("Имя и логин обязательны, пароль — минимум 6 символов")
        if clients.get_by_login(login) or managers.get_by_login(login) or administrators.get_by_login(login):
            raise ValueError("Такой логин уже занят")
        return managers.create(full_name.strip(), login.strip(), _hash_password(password))

auth = AuthService()

class TourService:
    def create(self, title, destination, price, available=1):
        if not title.strip() or not destination.strip():
            raise ValueError("Название тура и направление обязательны")
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        return tours.create(title.strip(), destination.strip(), price, available)

class BookingService:
    def create(self, client_id, tour_id):
        if not clients.get_by_id(client_id):
            raise ValueError("Клиент не найден")
        tour = tours.get_by_id(tour_id)
        if not tour:
            raise ValueError("Тур не найден")
        if not tour.available:
            raise ValueError("Этот тур сейчас недоступен")
        return bookings.create(client_id, tour_id)

    def pay(self, client_id, tour_id):
        client = clients.get_by_id(client_id)
        tour = tours.get_by_id(tour_id)
        if not client or not tour:
            raise ValueError("Клиент или тур не найден")
        if not tour.available:
            raise ValueError("Тур недоступен")
        with get_connection() as db:
            row = db.execute("SELECT balance FROM clients WHERE client_id=?", (client_id,)).fetchone()
            if row["balance"] < tour.price:
                raise ValueError("Недостаточно средств. Пополните баланс")
            db.execute("UPDATE clients SET balance=balance-? WHERE client_id=?", (tour.price, client_id))
            db.execute("INSERT INTO bookings(client_id,tour_id,booking_date,status,manager_id) VALUES(?,?,?,'Забронирована',NULL)",
                       (client_id, tour_id, date.today().isoformat()))

booking_service = BookingService()
tour_service = TourService()

# ======================= ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС ====================
def ask_int(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Ошибка: введите целое число.")
        return None


def show_tours():
    print("\nТуры:")
    for t in tours.get_all():
        print(f"{t.tour_id}. {t.title} — {t.destination}; цена: {t.price:.2f}; доступен: {'да' if t.available else 'нет'}")


def show_bookings():
    print("\nЗаявки:")
    for b in bookings.get_all():
        print(f"№{b['booking_id']}: {b['full_name']} — {b['title']}; дата {b['booking_date']}; статус {b['status']}; менеджер {b['manager_id'] or 'не назначен'}")


def client_menu(client):
    while True:
        current = clients.get_by_id(client.client_id)
        print(f"\n=== Меню клиента: {current.full_name} ===")
        print("1. Посмотреть туры\n2. Посмотреть баланс\n3. Пополнить баланс (имитация)\n4. Купить тур\n5. Мои данные\n0. Выйти")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                show_tours()
            elif choice == "2":
                print(f"Баланс: {current.balance:.2f}")
            elif choice == "3":
                amount = float(input("Сумма пополнения: "))
                if amount <= 0: raise ValueError("Сумма должна быть положительной")
                if not clients.change_balance(current.client_id, amount): raise ValueError("Не удалось пополнить баланс")
                print("Баланс пополнен (учебная имитация).")
            elif choice == "4":
                show_tours()
                tour_id = ask_int("ID тура: ")
                if tour_id is not None:
                    booking_service.pay(current.client_id, tour_id)
                    print("Оплата и заявка успешно оформлены.")
            elif choice == "5":
                print(current)
            elif choice == "0":
                break
            else: print("Нет такого пункта меню.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Ошибка: {error}")


def manager_menu(manager):
    while True:
        print(f"\n=== Меню менеджера: {manager.full_name} ===\n1. Посмотреть клиентов\n2. Посмотреть туры\n3. Посмотреть заявки\n4. Назначить себя на заявку\n0. Выйти")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            for c in clients.get_all(): print(c)
        elif choice == "2": show_tours()
        elif choice == "3": show_bookings()
        elif choice == "4":
            show_bookings()
            booking_id = ask_int("ID заявки: ")
            if booking_id is not None:
                if bookings.assign_manager(booking_id, manager.manager_id): print("Менеджер назначен.")
                else: print("Заявка не найдена.")
        elif choice == "0": break
        else: print("Нет такого пункта меню.")


def admin_menu(admin):
    while True:
        print(f"\n=== Меню администратора: {admin.full_name} ===")
        print("1. Клиенты\n2. Добавить тур\n3. Изменить доступность тура\n4. Заявки\n5. Создать менеджера\n6. Добавить клиента вручную\n7. Удалить клиента\n0. Выйти")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                for c in clients.get_all(): print(c)
            elif choice == "2":
                title = input("Название тура: "); destination = input("Направление: ")
                price = float(input("Цена: ")); tour_id = tour_service.create(title, destination, price)
                print(f"Тур добавлен, ID {tour_id}.")
            elif choice == "3":
                show_tours(); tour_id = ask_int("ID тура: ")
                available = ask_int("Доступен? 1 — да, 0 — нет: ")
                tour = tours.get_by_id(tour_id) if tour_id is not None else None
                if tour and available in (0, 1):
                    print("Обновлено." if tours.update(tour_id, tour.title, tour.destination, tour.price, available) else "Не удалось обновить.")
                else: print("Проверьте ID и значение доступности.")
            elif choice == "4": show_bookings()
            elif choice == "5":
                name = input("ФИО менеджера: "); login = input("Логин: "); password = input("Пароль (минимум 6 символов): ")
                print(f"Менеджер создан, ID {auth.create_manager(name, login, password)}.")
            elif choice == "6":
                name = input("ФИО: "); phone = input("Телефон: "); email = input("Email (необязательно): ")
                login = input("Логин: "); password = input("Пароль (минимум 6 символов): ")
                print(f"Клиент создан, ID {auth.register_client(name, phone, email, login, password)}.")
            elif choice == "7":
                for c in clients.get_all(): print(c.client_id, c.full_name, c.phone)
                client_id = ask_int("ID клиента: ")
                if client_id is not None:
                    try: deleted = clients.delete(client_id); print("Клиент удалён." if deleted else "Клиент не найден.")
                    except sqlite3.IntegrityError: print("Нельзя удалить клиента, у которого есть заявки.")
            elif choice == "0": break
            else: print("Нет такого пункта меню.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Ошибка: {error}")


def main():
    initialize_database()
    print("=== Учёт клиентов турфирмы ===")
    if not administrators.get_all():
        print("Первый запуск: создайте учётную запись администратора.")
        while True:
            try:
                name = input("ФИО администратора: ")
                login = input("Логин администратора: ")
                password = input("Пароль (минимум 6 символов): ")
                auth.create_first_admin(name, login, password)
                print("Администратор создан. Теперь войдите в систему.")
                break
            except (ValueError, sqlite3.IntegrityError) as error:
                print(f"Ошибка: {error}")
    while True:
        print("\n1. Войти\n2. Регистрация клиента\n0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                login = input("Логин: "); password = input("Пароль: ")
                result = auth.login(login, password)
                if not result: print("Неверный логин или пароль."); continue
                role, user = result
                if role == "Клиент": client_menu(user)
                elif role == "Менеджер": manager_menu(user)
                else: admin_menu(user)
            elif choice == "2":
                name = input("ФИО: "); phone = input("Телефон: "); email = input("Email (необязательно): ")
                login = input("Логин: "); password = input("Пароль (минимум 6 символов): ")
                client_id = auth.register_client(name, phone, email, login, password)
                print(f"Регистрация завершена. Ваш ID: {client_id}")
            elif choice == "0": break
            else: print("Нет такого пункта меню.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Ошибка: {error}")
    print("Работа программы завершена.")

if __name__ == "__main__":
    main()

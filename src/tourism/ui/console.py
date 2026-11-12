import sqlite3
from tourism.container import clients, tours, bookings, managers, administrators, auth_service, booking_service, tour_service, export_service


def ask_int(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Ошибка: введите целое число.")
        return None


def ask_float(prompt):
    try:
        return float(input(prompt).strip().replace(",", "."))
    except ValueError:
        print("Ошибка: введите число.")
        return None


def print_section(title):
    print("\n" + "=" * 58)
    print(title.center(58))
    print("=" * 58)


def print_client(client, show_hash=False):
    print("-" * 58)
    print(f"ID:          {client.client_id}")
    print(f"ФИО:         {client.full_name}")
    print(f"Телефон:     {client.phone}")
    print(f"Email:       {client.email or 'не указан'}")
    print(f"Логин:       {client.login or 'не задан'}")
    print(f"Баланс:      {client.balance:.2f} руб.")
    if show_hash:
        print(f"Хеш пароля:  {client.password_hash or 'не задан'}")
    print("-" * 58)


def show_clients(show_hash=False):
    print_section("СПИСОК КЛИЕНТОВ")
    all_clients = clients.get_all()
    if not all_clients:
        print("Клиентов пока нет.")
        return
    for client in all_clients:
        print_client(client, show_hash)


def show_tours():
    print_section("СПИСОК ТУРОВ")
    all_tours = tours.get_all()
    if not all_tours:
        print("Туры не найдены.")
        return
    for tour in all_tours:
        print("-" * 58)
        print(f"ID:           {tour.tour_id}")
        print(f"Название:     {tour.title}")
        print(f"Направление:  {tour.destination}")
        print(f"Стоимость:    {tour.price:.2f} руб.")
        print(f"Доступность:  {'доступен' if tour.available else 'недоступен'}")
    print("-" * 58)


def show_bookings():
    print_section("СПИСОК ЗАЯВОК")
    all_bookings = bookings.get_all()
    if not all_bookings:
        print("Заявок пока нет.")
        return
    for booking in all_bookings:
        client = clients.get_by_id(booking.client_id)
        tour = tours.get_by_id(booking.tour_id)
        print("-" * 58)
        print(f"Номер заявки: {booking.booking_id}")
        print(f"Клиент:       {client.full_name if client else 'Клиент удалён'}")
        print(f"Тур:          {tour.title if tour else 'Тур удалён'}")
        print(f"Дата:         {booking.booking_date}")
        print(f"Статус:       {booking.status}")
        print(f"Менеджер ID:  {booking.manager_id or 'не назначен'}")
    print("-" * 58)


def client_menu(client):
    while True:
        current = clients.get_by_id(client.client_id)
        if not current:
            print("Учётная запись клиента не найдена.")
            return
        print(f"\n=== Меню клиента: {current.full_name} ===")
        print("1. Посмотреть туры\n2. Посмотреть баланс\n3. Пополнить баланс (имитация)\n4. Купить тур\n5. Мои данные\n0. Выйти")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                show_tours()
            elif choice == "2":
                print(f"Баланс: {current.balance:.2f}")
            elif choice == "3":
                amount = ask_float("Сумма пополнения: ")
                if amount is not None:
                    if amount <= 0:
                        raise ValueError("Сумма должна быть положительной")
                    if not clients.change_balance(current.client_id, amount):
                        raise ValueError("Не удалось пополнить баланс")
                    print("Баланс пополнен (учебная имитация).")
            elif choice == "4":
                show_tours()
                tour_id = ask_int("ID тура: ")
                if tour_id is not None:
                    booking_service.pay(current.client_id, tour_id)
                    print("Оплата и заявка успешно оформлены.")
            elif choice == "5":
                print_section("МОИ ДАННЫЕ")
                print_client(current)
            elif choice == "0":
                return
            else:
                print("Нет такого пункта меню.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Ошибка: {error}")


def manager_menu(manager):
    while True:
        print(f"\n=== Меню менеджера: {manager.full_name} ===\n1. Посмотреть клиентов\n2. Посмотреть туры\n3. Посмотреть заявки\n4. Назначить себя на заявку\n0. Выйти")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            show_clients()
        elif choice == "2": show_tours()
        elif choice == "3": show_bookings()
        elif choice == "4":
            show_bookings()
            booking_id = ask_int("ID заявки: ")
            if booking_id is not None:
                print("Менеджер назначен." if bookings.assign_manager(booking_id, manager.manager_id) else "Заявка не найдена.")
        elif choice == "0": return
        else: print("Нет такого пункта меню.")


def admin_menu(admin):
    while True:
        print(f"\n=== Меню администратора: {admin.full_name} ===")
        print("1. Клиенты\n2. Добавить тур\n3. Изменить доступность тура\n4. Заявки\n5. Создать менеджера\n6. Добавить клиента вручную\n7. Удалить клиента\n8. Просмотреть хеши паролей клиентов\n9. Экспортировать клиентов в JSON, CSV, XML и YAML\n0. Выйти")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                show_clients()
            elif choice == "2":
                title = input("Название тура: "); destination = input("Направление: "); price = ask_float("Цена: ")
                if price is not None: print(f"Тур добавлен, ID {tour_service.create(title, destination, price)}.")
            elif choice == "3":
                show_tours(); tour_id = ask_int("ID тура: "); available = ask_int("Доступен? 1 — да, 0 — нет: ")
                if tour_id is not None and available is not None:
                    tour_service.set_availability(tour_id, available)
                    print("Доступность обновлена.")
            elif choice == "4": show_bookings()
            elif choice == "5":
                name = input("ФИО менеджера: "); login = input("Логин: "); password = input("Пароль (минимум 6 символов): ")
                print(f"Менеджер создан, ID {auth_service.create_manager(name, login, password)}.")
            elif choice == "6":
                name = input("ФИО: "); phone = input("Телефон: "); email = input("Email (необязательно): ")
                login = input("Логин: "); password = input("Пароль (минимум 6 символов): ")
                print(f"Клиент создан, ID {auth_service.register_client(name, phone, email, login, password)}.")
            elif choice == "7":
                print_section("КЛИЕНТЫ ДЛЯ УДАЛЕНИЯ")
                for client in clients.get_all(): print(f"ID: {client.client_id} | {client.full_name} | {client.phone}")
                client_id = ask_int("ID клиента: ")
                if client_id is not None:
                    print("Клиент удалён." if clients.delete(client_id) else "Клиент не найден.")
            elif choice == "8":
                print("Внимание: хеши паролей доступны только в этом разделе администратора.")
                show_clients(show_hash=True)
            elif choice == "9":
                paths = export_service.export_all()
                print_section("ЭКСПОРТ ЗАВЕРШЁН")
                print("Данные клиентов и связанные заявки сохранены в папку out:")
                for path in paths:
                    print(f"- {path.name}")
            elif choice == "0": return
            else: print("Нет такого пункта меню.")
        except (ValueError, sqlite3.IntegrityError) as error:
            print(f"Ошибка: {error}")


def run():
    print("=== Учёт клиентов турфирмы ===")
    if not administrators.get_all():
        print("Первый запуск: создайте учётную запись администратора.")
        while True:
            try:
                name = input("ФИО администратора: "); login = input("Логин администратора: "); password = input("Пароль (минимум 6 символов): ")
                auth_service.create_first_admin(name, login, password)
                print("Администратор создан. Теперь войдите в систему.")
                break
            except (ValueError, sqlite3.IntegrityError) as error: print(f"Ошибка: {error}")
    while True:
        print("\n1. Войти\n2. Регистрация клиента\n0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                result = auth_service.login(input("Логин: ").strip(), input("Пароль: "))
                if not result: print("Неверный логин или пароль."); continue
                role, user = result
                if role == "Клиент": client_menu(user)
                elif role == "Менеджер": manager_menu(user)
                else: admin_menu(user)
            elif choice == "2":
                name = input("ФИО: "); phone = input("Телефон: "); email = input("Email (необязательно): ")
                login = input("Логин: "); password = input("Пароль (минимум 6 символов): ")
                client_id = auth_service.register_client(name, phone, email, login, password)
                print(f"Регистрация завершена. Ваш ID: {client_id}")
            elif choice == "0": break
            else: print("Нет такого пункта меню.")
        except (ValueError, sqlite3.IntegrityError) as error: print(f"Ошибка: {error}")
    print("Работа программы завершена.")

from datetime import date

class BookingService:
    def __init__(self, client_repository, tour_repository, booking_repository):
        self.clients = client_repository
        self.tours = tour_repository
        self.bookings = booking_repository

    def create(self, client_id, tour_id):
        if not self.clients.get_by_id(client_id):
            raise ValueError("Клиент не найден")
        tour = self.tours.get_by_id(tour_id)
        if not tour:
            raise ValueError("Тур не найден")
        if not tour.available:
            raise ValueError("Этот тур сейчас недоступен")
        return self.bookings.create(client_id, tour_id)

    def pay(self, client_id, tour_id):
        client = self.clients.get_by_id(client_id)
        tour = self.tours.get_by_id(tour_id)
        if not client or not tour:
            raise ValueError("Клиент или тур не найден")
        if not tour.available:
            raise ValueError("Тур недоступен")
        # Операция списания и создания заявки выполняется методом репозитория,
        # который обеспечивает транзакционность. Сервис не знает о SQL/SQLite.
        return self.bookings.pay_booking(client_id, tour_id, tour.price, date.today().isoformat())

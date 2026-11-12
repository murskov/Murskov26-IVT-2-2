class TourService:
    def __init__(self, tour_repository):
        self.tours = tour_repository

    def create(self, title, destination, price, available=1):
        if not title.strip() or not destination.strip():
            raise ValueError("Название тура и направление обязательны")
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if available not in (0, 1):
            raise ValueError("Доступность должна быть равна 0 или 1")
        return self.tours.create(title.strip(), destination.strip(), price, available)

    def set_availability(self, tour_id, available):
        if available not in (0, 1):
            raise ValueError("Доступность должна быть равна 0 или 1")
        if not self.tours.get_by_id(tour_id):
            raise ValueError("Тур не найден")
        return self.tours.set_availability(tour_id, available)

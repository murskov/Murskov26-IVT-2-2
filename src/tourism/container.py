from tourism.repositories import ClientRepository, TourRepository, BookingRepository, ManagerRepository, AdministratorRepository, ExportRepository
from tourism.services import AuthService, BookingService, TourService, ExportService

clients = ClientRepository()
tours = TourRepository()
bookings = BookingRepository()
managers = ManagerRepository()
administrators = AdministratorRepository()

auth_service = AuthService(clients, managers, administrators)
booking_service = BookingService(clients, tours, bookings)
tour_service = TourService(tours)

export_service = ExportService(ExportRepository())

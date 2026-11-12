from dataclasses import dataclass

@dataclass
class Booking:
    booking_id: int
    client_id: int
    tour_id: int
    booking_date: str
    status: str
    manager_id: int | None = None

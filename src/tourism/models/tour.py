from dataclasses import dataclass

@dataclass
class Tour:
    tour_id: int
    title: str
    destination: str
    price: float
    available: int

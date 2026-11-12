from dataclasses import dataclass

@dataclass
class Client:
    client_id: int
    full_name: str
    phone: str
    email: str | None = None
    login: str | None = None
    password_hash: str | None = None
    balance: float = 0.0

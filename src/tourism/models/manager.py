from dataclasses import dataclass

@dataclass
class Manager:
    manager_id: int
    full_name: str
    login: str
    password_hash: str

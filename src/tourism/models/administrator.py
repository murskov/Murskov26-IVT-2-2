from dataclasses import dataclass

@dataclass
class Administrator:
    admin_id: int
    full_name: str
    login: str
    password_hash: str

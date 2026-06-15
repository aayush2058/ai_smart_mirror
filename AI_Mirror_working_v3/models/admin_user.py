from dataclasses import dataclass
from typing import Optional


@dataclass
class AdminUser:
    username: str
    password_hash: str
    active: bool = True
    id: Optional[int] = None
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

@dataclass
class User:
    id: UUID
    username: str
    password: str
    email: Optional[str]
    fullname: Optional[str]
    phone_number: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, username: str, password: str, role: str = 'USER', email: str = None, 
               fullname: str = None, phone_number: str = None, 
               gender: str = None, address: str = None) -> 'User':
        now = datetime.now()
        return cls(
            id=uuid4(),
            username=username,
            password=password,
            email=email,
            fullname=fullname,
            phone_number=phone_number,
            gender=gender,
            address=address,
            role=role,
            is_active=False, # Default to inactive until activated
            created_at=now,
            updated_at=now
        )

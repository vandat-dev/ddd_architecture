from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from app.modules.user.domain.entities import User

class IUserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_all(self, skip: int, limit: int) -> List[User]:
        pass

    @abstractmethod
    async def get_with_count(self, skip: int, limit: int) -> Tuple[List[User], int]:
        pass

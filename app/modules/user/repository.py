import asyncio
from typing import Tuple, Optional, List
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.model import User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email for login"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by UUID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> User:
        """Create new user"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        await self.db.commit()
        return user

    async def get_all_users(self, skip: int, limit: int) -> List[User]:
        """Get paginated users without count"""
        stmt = select(User).where(User.is_active == True).order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return users

    async def get_users_with_count(self, skip: int, limit: int) -> Tuple[List[User], int]:
        """
        Retrieve a paginated list of active users along with the total count.
        Combines logic from `get_all_users` and `get_total_users`.
        """
        count_stmt = select(func.count(User.id)).where(User.is_active.is_(True))

        data_stmt = (
            select(User)
            .where(User.is_active.is_(True))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Execute both queries concurrently for better performance
        count_result, data_result = await asyncio.gather(
            self.db.execute(count_stmt),
            self.db.execute(data_stmt),
        )

        total = count_result.scalar()
        users = data_result.scalars().all()
        return users, total

    async def update_user(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user by ID"""
        stmt = update(User).where(User.id == user_id).values(**user_data).returning(User)
        result = await self.db.execute(stmt)
        updated_user = result.scalar_one_or_none()
        if updated_user:
            await self.db.refresh(updated_user)
            await self.db.commit()
        return updated_user

    async def delete_user(self, user_id: UUID) -> Optional[UUID]:
        """Soft delete user (set is_active=False)"""
        stmt = update(User).where(User.id == user_id).values(is_active=False).returning(User.id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

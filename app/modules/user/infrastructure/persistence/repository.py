import asyncio
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.domain.entities import User
from app.modules.user.domain.interfaces import IUserRepository
from app.modules.user.infrastructure.persistence.models import UserModel
from app.modules.user.infrastructure.persistence.mappers import to_domain, to_model

class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model)

    async def find_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model)

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model)

    async def create(self, user: User) -> User:
        model = to_model(user)
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        await self.db.commit()
        return to_domain(model)

    async def update(self, user: User) -> User:
        # In a real DDD approach, we might track changes in the entity and apply them.
        # Here we just update all fields for simplicity or use the model's state.
        # However, since we are passing a Domain Entity, we need to update the DB record matching its ID.
        
        # Note: This is a simplified update. 
        # Ideally we fetch the model, update fields, and let SQLAlchemy handle the rest.
        stmt = update(UserModel).where(UserModel.id == user.id).values(
            username=user.username,
            email=user.email,
            fullname=user.fullname,
            phone_number=user.phone_number,
            gender=user.gender,
            address=user.address,
            role=user.role,
            is_active=user.is_active,
            updated_at=func.now() # Update timestamp
        ).returning(UserModel)
        
        result = await self.db.execute(stmt)
        updated_model = result.scalar_one_or_none()
        await self.db.commit() # Service layer handles commit
        return to_domain(updated_model)

    async def delete(self, user_id: UUID) -> bool:
        stmt = update(UserModel).where(UserModel.id == user_id).values(is_active=False)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def get_all(self, skip: int, limit: int) -> List[User]:
        stmt = select(UserModel).where(UserModel.is_active == True).order_by(UserModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [to_domain(m) for m in models]

    async def get_with_count(self, skip: int, limit: int) -> Tuple[List[User], int]:
        count_stmt = select(func.count(UserModel.id)).where(UserModel.is_active.is_(True))
        data_stmt = (
            select(UserModel)
            .where(UserModel.is_active.is_(True))
            .order_by(UserModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        count_result, data_result = await asyncio.gather(
            self.db.execute(count_stmt),
            self.db.execute(data_stmt),
        )

        total = count_result.scalar()
        models = data_result.scalars().all()
        return [to_domain(m) for m in models], total

import asyncio
import argparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, or_
from passlib.context import CryptContext

from app.core.setting import settings
from app.modules.user.infrastructure.persistence.models import UserModel

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin(username: str, email: str, password: str, role="ADMIN"):
    # Create async engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False
    )
    
    # Create session factory
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if user already exists
            stmt = select(UserModel).where(or_(UserModel.username == username, UserModel.email == email))
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print("⚠️ Admin đã tồn tại:", existing.username)
                return

            # Hash password
            hashed_password = pwd_context.hash(password)

            # Create user
            new_user = UserModel(
                username=username,
                email=email,
                # password=hashed_password, # UserModel does not have password!
                role=role,
                is_active=True
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            print("✅ Admin created:", new_user.username)

        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating admin: {e}")
            raise
        finally:
            await session.close()
    
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--username", required=True, help="Username of the admin")
    parser.add_argument("--email", required=True, help="Email of the admin")
    parser.add_argument("--password", required=True, help="Password of the admin")

    args = parser.parse_args()

    asyncio.run(create_admin(args.username, args.email, args.password))

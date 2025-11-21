from fastapi import Depends

from app.core.setting import settings
from app.initialize.database import get_session
from app.modules.user.infrastructure.persistence.repository import SQLAlchemyUserRepository
from app.modules.auth.security import TokenService
from app.modules.user.application.services import AuthService


def get_auth_repository(db=Depends(get_session)):
    return SQLAlchemyUserRepository(db)


def get_token_service():
    return TokenService(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM, settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES,
                        settings.REFRESH_TOKEN_EXPIRES_IN_DAYS)


def get_auth_service(
    user_repository=Depends(get_auth_repository),
    token_service=Depends(get_token_service)
) -> AuthService:
    return AuthService(user_repository, token_service)

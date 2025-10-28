from fastapi import Depends

from app.core.setting import settings
from app.initialize.database import get_session
from app.modules.user.repository import AuthRepository
from app.modules.auth.security import TokenService
from app.modules.user.service import AuthService


def get_auth_repository(db=Depends(get_session)):
    return AuthRepository(db)


def get_token_service():
    return TokenService(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM, settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES,
                        settings.REFRESH_TOKEN_EXPIRES_IN_DAYS)


def get_auth_service(auth_repository: AuthRepository = Depends(get_auth_repository),
                     token_service: TokenService = Depends(get_token_service)):
    return AuthService(auth_repository, token_service)

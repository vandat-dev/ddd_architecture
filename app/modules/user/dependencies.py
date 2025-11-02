from fastapi import Depends

from app.core.setting import settings
from app.initialize.database import get_session
from app.modules.user.repository import AuthRepository
from app.modules.auth.security import TokenService
from app.modules.auth.keycloak_admin import KeycloakAdminService
from app.modules.user.service import AuthService


def get_auth_repository(db=Depends(get_session)):
    return AuthRepository(db)


def get_token_service():
    return TokenService()


def get_keycloak_admin_service():
    return KeycloakAdminService()


def get_auth_service(auth_repository: AuthRepository = Depends(get_auth_repository),
                     token_service: TokenService = Depends(get_token_service),
                     keycloak_admin_service: KeycloakAdminService = Depends(get_keycloak_admin_service)):
    return AuthService(auth_repository, token_service, keycloak_admin_service)

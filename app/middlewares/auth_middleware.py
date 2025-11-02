from datetime import timedelta
from uuid import UUID
import logging
from fastapi import Request, HTTPException, Response
from fastapi.params import Depends

from app.constant.enums import UserRole
from app.core.app_status import AppStatus
from app.core.setting import settings
from app.modules.user.model import User
from app.modules.user.dependencies import get_token_service, get_auth_repository
from app.modules.user.repository import AuthRepository
from app.modules.auth.security import TokenService, CookieService
from app.utils.response import error_exception_handler

logger = logging.getLogger(__name__)


class AuthMiddleware:

    @classmethod
    async def get_current_user(cls, request: Request, response: Response,
                               token_service: TokenService = Depends(get_token_service),
                               auth_repo: AuthRepository = Depends(get_auth_repository)):
        try:
            token = CookieService.get_token_from_cookie("access_token", request)
            claims = token_service.validate_token(token)
            if not claims:
                user = await cls.handle_refresh_token_valid(request, response, token_service, auth_repo)
                return user
            user = await auth_repo.find_user_by_id(UUID(claims.get("sub")))
            return user

        except Exception:
            raise error_exception_handler(AppStatus.UNAUTHORIZED, headers=response.headers)

    @staticmethod
    async def handle_refresh_token_valid(request, response, token_service, auth_repo):
        logger.info("AuthMiddleware.handle_refresh_token_valid - handle_refresh_token_valid")
        refresh_token = CookieService.get_token_from_cookie("refresh_token", request)
        if not refresh_token:
            raise error_exception_handler(AppStatus.UNAUTHORIZED, headers=response.headers)
        tokens = await token_service.generate_refresh_tokens(refresh_token)
        if not tokens:
            CookieService.clear_cookie(response)
            raise error_exception_handler(AppStatus.UNAUTHORIZED, headers=response.headers)
        claims = token_service.validate_token(tokens.get("access_token"))
        if not claims:
            raise error_exception_handler(AppStatus.UNAUTHORIZED, headers=response.headers)
        origin = CookieService.get_origin_from_request(request)
        user = await auth_repo.find_user_by_id(UUID(claims.get("sub")))
        CookieService.set_cookie(response, "access_token", tokens.get("access_token"), origin,
                                 max_age=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES))
        CookieService.set_cookie(response, "refresh_token", tokens.get("refresh_token"), origin,
                                 max_age=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN_MINUTES))

        return user

    @classmethod
    def is_user(cls):
        async def dependency(auth_info: User = Depends(cls.get_current_user), response: Response = None):
            if not auth_info.is_active:
                '''
                headers=response.headers
                Cookies are still being set before the error is raised.
                '''
                raise HTTPException(status_code=403, detail={
                    "error_code": AppStatus.FORBIDDEN.error_code,
                    "message": AppStatus.FORBIDDEN.message
                }, headers=response.headers)
            return auth_info

        return dependency

    @classmethod
    def is_admin(cls):
        async def dependency(current_user: User = Depends(cls.get_current_user), response: Response = None):
            if current_user.role != UserRole.ADMIN:
                '''
                headers=response.headers
                Cookies are still being set before the error is raised.
                '''
                raise HTTPException(status_code=403, detail={
                    "error_code": AppStatus.FORBIDDEN.error_code,
                    "message": AppStatus.FORBIDDEN.message
                }, headers=response.headers)
            return current_user

        return dependency

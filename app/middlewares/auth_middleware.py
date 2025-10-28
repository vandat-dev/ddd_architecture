from datetime import timedelta
from uuid import UUID

from fastapi import Request, HTTPException, Response
from fastapi.params import Depends

from app.constant.enums import UserRole
from app.core.app_status import AppStatus
from app.core.setting import settings
from app.modules.user.model import User
from app.modules.user.dependencies import get_token_service, get_auth_repository
from app.modules.user.repository import AuthRepository
from app.modules.user.security import TokenService, CookieService
from app.utils.response import error_exception_handler


class AuthMiddleware:

    @classmethod
    async def get_current_user(cls, request: Request, response: Response,
                               token_service: TokenService = Depends(get_token_service),
                               auth_repo: AuthRepository = Depends(get_auth_repository)):
        try:
            token = CookieService.get_token_from_cookie("access_token", request)
            claims = token_service.validate_token(token)
            if not claims:
                refresh_token = CookieService.get_token_from_cookie("refresh_token", request)
                refresh_payload = token_service.validate_token(refresh_token)
                if not refresh_payload:
                    raise error_exception_handler(AppStatus.UNAUTHORIZED)
                user = await auth_repo.find_user_by_id(UUID(refresh_payload.get("sub")))
                access_token = token_service.refresh_access_token(refresh_token, user)
                origin = CookieService.get_origin_from_request(request)
                CookieService.set_cookie(response, "access_token", access_token, origin,
                                         max_age=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES))
                return user
            user = await auth_repo.find_user_by_id(UUID(claims.get("sub")))
            return user

        except Exception:
            raise error_exception_handler(AppStatus.UNAUTHORIZED)

    @classmethod
    def is_user(cls):
        def dependency(auth_info: User = Depends(cls.get_current_user)):
            if not auth_info.is_active:
                raise HTTPException(status_code=403, detail={
                    "error_code": AppStatus.FORBIDDEN.error_code,
                    "message": AppStatus.FORBIDDEN.message
                })
            return auth_info

        return dependency

    @classmethod
    def is_admin(cls):
        def dependency(current_user: User = Depends(cls.get_current_user)):
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail={
                    "error_code": AppStatus.FORBIDDEN.error_code,
                    "message": AppStatus.FORBIDDEN.message
                })
            return current_user

        return dependency

import logging
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from app.core.app_status import AppStatus
from app.core.setting import settings
from app.modules.user.dependencies import get_auth_service
from app.middlewares.auth_middleware import AuthMiddleware
from app.modules.user.schemas import LoginSchema, RegisterSchema, UserUpdateSchema, UserFilterSchema
from app.modules.auth.security import CookieService
from app.modules.user.service import AuthService
from app.utils.response import handle_response

logger = logging.getLogger(__name__)
auth_router = APIRouter()
user_router = APIRouter()


@auth_router.post("/register")
async def register(req: RegisterSchema, auth_service: AuthService = Depends(get_auth_service),
                   _=Depends(AuthMiddleware.is_admin())):
    return await auth_service.register(req)


@auth_router.post("/login")
async def login(request: Request, response: Response, code: str,
                auth_service: AuthService = Depends(get_auth_service)):
    tokens = await auth_service.exchange_code_for_token(code)

    CookieService.set_cookie(response, 'access_token', tokens.get("access_token"),
                             request_origin=request.headers.get("origin"),
                             max_age=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES))
    CookieService.set_cookie(response, 'refresh_token', tokens.get("refresh_token"),
                             request_origin=request.headers.get("origin"),
                             max_age=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN_MINUTES))
    return handle_response(app_status=AppStatus.LOGIN_SUCCESS)


@auth_router.get("/me")
async def me(user: AuthMiddleware = Depends(AuthMiddleware.get_current_user)):
    return user


@auth_router.post("/logout")
async def logout(response: Response, _=Depends(AuthMiddleware.get_current_user)):
    CookieService.clear_cookie(response)
    return handle_response(app_status=AppStatus.LOGOUT_SUCCESS)


@user_router.get("")
async def get_all_users(skip: int = 0, limit: int = 10,
                        user_filter=Depends(UserFilterSchema),
                        auth_service: AuthService = Depends(get_auth_service),
                        _: AuthMiddleware = Depends(AuthMiddleware.is_admin())):
    response = await auth_service.get_all_users(skip, limit)
    return handle_response(response=response)


@user_router.put("/{user_id}")
async def update_user(user_id: UUID, user_data: UserUpdateSchema,
                      auth_service: AuthService = Depends(get_auth_service),
                      _: AuthMiddleware = Depends(AuthMiddleware.is_user())):
    users = await auth_service.update_user(user_id, user_data)
    return users


@user_router.delete("/{user_id}")
async def delete_user(user_id: UUID,
                      auth_service: AuthService = Depends(get_auth_service),
                      _: AuthMiddleware = Depends(AuthMiddleware.is_user())):
    users = await auth_service.delete_user(user_id)
    return users

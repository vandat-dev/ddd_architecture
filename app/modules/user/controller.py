import logging
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.core.app_status import AppStatus
from app.core.setting import settings
from app.modules.user.dependencies import get_auth_service
from app.middlewares.auth_middleware import AuthMiddleware
from app.modules.user.schemas import LoginSchema, RegisterSchema, UserUpdateSchema, UserFilterSchema
from app.modules.user.security import CookieService
from app.modules.user.service import AuthService
from app.utils.response import handle_response

logger = logging.getLogger(__name__)
auth_router = APIRouter()
user_router = APIRouter()


@auth_router.post("/register")
async def register(req: RegisterSchema, auth_service: AuthService = Depends(get_auth_service),
                   _=Depends(AuthMiddleware.is_user())):
    return await auth_service.register(req)


@auth_router.post("/login")
async def login(request: Request, user_login: LoginSchema,
                auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.login(user_login.email, user_login.password)
    response = handle_response(app_status=AppStatus.LOGIN_SUCCESS)
    CookieService.set_cookie(response, 'access_token', token.get("access_token"),
                             request_origin=request.headers.get("origin"),
                             max_age=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN_MINUTES))
    CookieService.set_cookie(response, 'refresh_token', token.get("refresh_token"),
                             request_origin=request.headers.get("origin"),
                             max_age=timedelta(days=settings.REFRESH_TOKEN_EXPIRES_IN_DAYS))
    return response


@auth_router.get("/me")
async def me(user: AuthMiddleware = Depends(AuthMiddleware.get_current_user)):
    return user


@auth_router.post("/logout")
async def logout(_=Depends(AuthMiddleware.get_current_user)):
    response = handle_response(app_status=AppStatus.LOGOUT_SUCCESS)
    CookieService.clear_cookie(response)
    return response


@user_router.get("")
async def get_all_users(skip: int = 0, limit: int = 10,
                        user_filter=Depends(UserFilterSchema),
                        auth_service: AuthService = Depends(get_auth_service),
                        _: AuthMiddleware = Depends(AuthMiddleware.is_user())):
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

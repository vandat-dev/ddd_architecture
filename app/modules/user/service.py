import logging
from uuid import UUID

from app.core.app_status import AppStatus
from app.modules.user.schemas import RegisterSchema, UserUpdateSchema
from app.utils.hasher import hash_password, verify_password
from app.utils.response import error_exception_handler, handle_response

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository, token_service, keycloak_admin_service):
        self.user_repository = user_repository
        self.token_service = token_service
        self.keycloak_admin_service = keycloak_admin_service

    async def exchange_code_for_token(self, code: str):
        result = await self.token_service.exchange_code_for_token(code)
        return result

    async def register(self, param: RegisterSchema):
        # Check if user already exists in local database
        if await self.user_repository.find_user_by_email(param.email):
            raise error_exception_handler(app_status=AppStatus.ERROR_USER_ALREADY_EXISTS)

        if await self.user_repository.find_user_by_username(param.username):
            raise error_exception_handler(app_status=AppStatus.ERROR_USER_ALREADY_EXISTS)

        # Create user in Keycloak first and get the sub
        user_data_for_keycloak = param.model_dump(exclude_unset=True, exclude_none=True)

        keycloak_sub = await self.keycloak_admin_service.create_user(user_data_for_keycloak)

        # Create user in local database
        user_data_for_keycloak["id"] = keycloak_sub
        del user_data_for_keycloak["password"]
        user = await self.user_repository.create_user(user_data_for_keycloak)

        logger.info(f"Successfully registered user: {user.username} with Keycloak sub: {keycloak_sub}")
        return handle_response(app_status=AppStatus.SUCCESS, response=user.to_dict())

    async def get_all_users(self, skip: int, limit: int):
        logger.info("AuthService.login - Get all users")
        users, total = await self.user_repository.get_users_with_count(skip, limit)
        users_dict = [user.to_dict() for user in users]
        return {"total": total, "users": users_dict}

    async def update_user(self, user_id: UUID, user_data: UserUpdateSchema):
        data = user_data.model_dump(exclude_unset=True, exclude_none=True)
        if data.get("password"):
            data["password"] = hash_password(data["password"])

        result = await self.user_repository.update_user(user_id, data)
        return result

    async def delete_user(self, user_id: UUID):
        result = await self.user_repository.delete_user(user_id)
        if not result:
            raise error_exception_handler(AppStatus.ERROR_USER_NOT_FOUND)
        return handle_response(app_status=AppStatus.SUCCESS)

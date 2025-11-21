import logging
from uuid import UUID

from app.core.app_status import AppStatus
from app.modules.user.application.dtos import RegisterSchema, UserUpdateSchema
from app.modules.user.domain.entities import User
from app.modules.user.domain.interfaces import IUserRepository
from app.utils.hasher import hash_password, verify_password
from app.utils.response import error_exception_handler, handle_response

logger = logging.getLogger(__name__)



class AuthService:
    def __init__(self, user_repository: IUserRepository, token_service):
        self.user_repository = user_repository
        self.token_service = token_service

    async def login(self, email: str, password: str):
        user = await self.user_repository.find_by_email(email)
        if not user:
            raise error_exception_handler(app_status=AppStatus.ERROR_USER_NOT_FOUND)

        # Verify password
        if not verify_password(password, user.password):
            raise error_exception_handler(app_status=AppStatus.ERROR_USER_NOT_FOUND)  # Same error for security

        return self.token_service.generate_token_pair(user)

    async def register(self, param: RegisterSchema):
        # Check if user already exists in local database
        if await self.user_repository.find_by_email(param.email):
            raise error_exception_handler(app_status=AppStatus.ERROR_USER_ALREADY_EXISTS)

        if await self.user_repository.find_by_username(param.username):
            raise error_exception_handler(app_status=AppStatus.ERROR_USER_ALREADY_EXISTS)

        # Hash password
        hashed_password = hash_password(param.password)

        # Create user entity
        user_entity = User.create(
            username=param.username,
            password=hashed_password,
            email=param.email,
            fullname=param.fullname,
            phone_number=param.phone_number,
            role=param.role if param.role else 'USER',
        )

        created_user = await self.user_repository.create(user_entity)
        logger.info(f"Successfully registered user: {created_user.username}")
        
        return handle_response(app_status=AppStatus.SUCCESS, response=self._user_to_dict(created_user))

    async def get_all_users(self, skip: int, limit: int):
        logger.info("AuthService.login - Get all users")
        users, total = await self.user_repository.get_with_count(skip, limit)
        users_dict = [self._user_to_dict(user) for user in users]
        return {"total": total, "users": users_dict}

    async def update_user(self, user_id: UUID, user_data: UserUpdateSchema):
        # First find the user
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise error_exception_handler(AppStatus.ERROR_USER_NOT_FOUND)

        data = user_data.model_dump(exclude_unset=True, exclude_none=True)

        # Update fields
        if data.get("password"):
            user.password = hash_password(data["password"])

        for key, value in data.items():
            if hasattr(user, key) and key != 'password':
                setattr(user, key, value)

        updated_user = await self.user_repository.update(user)
        return self._user_to_dict(updated_user)

    async def delete_user(self, user_id: UUID):
        result = await self.user_repository.delete(user_id)
        if not result:
            raise error_exception_handler(AppStatus.ERROR_USER_NOT_FOUND)
        return handle_response(app_status=AppStatus.SUCCESS)

    def _user_to_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "fullname": user.fullname,
            "phone_number": user.phone_number,
            "gender": user.gender,
            "address": user.address,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

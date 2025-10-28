from enum import Enum

from app.constant import common_status_codes as common
from app.modules.user import user_status_codes as user


class AppStatus(Enum):
    # common
    SUCCESS = common.SUCCESS
    BAD_REQUEST = common.BAD_REQUEST
    NOT_FOUND = common.NOT_FOUND
    FORBIDDEN = common.FORBIDDEN
    ERROR_INTERNAL_SERVER_ERROR = common.ERROR_INTERNAL_SERVER_ERROR
    UNAUTHORIZED = common.UNAUTHORIZED

    # user
    LOGIN_SUCCESS = user.LOGIN_SUCCESS
    LOGOUT_SUCCESS = user.LOGOUT_SUCCESS

    ERROR_LOGIN_INVALID = user.ERROR_LOGIN_INVALID
    ERROR_USER_INACTIVE = user.ERROR_USER_INACTIVE
    ERROR_USER_ALREADY_EXISTS = user.ERROR_USER_ALREADY_EXISTS
    ERROR_USER_PHONE_ALREADY_EXISTS = user.ERROR_USER_PHONE_ALREADY_EXISTS
    ERROR_INVALID_ROLE = user.ERROR_INVALID_ROLE
    ERROR_USER_NOT_FOUND = user.ERROR_USER_NOT_FOUND
    ERROR_USER_DATA_IMPORT = user.ERROR_USER_DATA_IMPORT
    ERROR_USER_MISSING_COLUMN = user.ERROR_USER_MISSING_COLUMN

    @property
    def status_code(self):
        return self.value[0]

    @property
    def custom_status_code(self):
        return self.value[1]

    @property
    def error_code(self):
        return self.value[2]

    @property
    def message(self):
        return self.value[3]

    @property
    def meta(self):
        return {
            "custom_status_code": self.custom_status_code,
            "error_code": self.error_code,
            "message": self.message,
        }

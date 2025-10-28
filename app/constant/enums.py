from enum import Enum


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    ENTRY = "ENTRY"
    CHECKER = "CHECKER"

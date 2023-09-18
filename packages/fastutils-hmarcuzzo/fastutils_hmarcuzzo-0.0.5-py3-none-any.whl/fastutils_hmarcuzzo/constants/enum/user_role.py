from enum import Enum as PyEnum

from sqlalchemy import Enum


class UserRole(PyEnum):
    ADMIN = "ADMIN"
    NUTRITIONIST = "NUTRITIONIST"
    USER = "USER"


UserRole = Enum(UserRole, name="user-role")

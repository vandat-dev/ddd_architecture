from app.modules.user.domain.entities import User
from app.modules.user.infrastructure.persistence.models import UserModel

def to_domain(model: UserModel) -> User:
    if not model:
        return None
    return User(
        id=model.id,
        username=model.username,
        password=model.password,
        email=model.email,
        fullname=model.fullname,
        phone_number=model.phone_number,
        gender=model.gender,
        address=model.address,
        role=model.role,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at
    )

def to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        username=entity.username,
        password=entity.password,
        email=entity.email,
        fullname=entity.fullname,
        phone_number=entity.phone_number,
        gender=entity.gender,
        address=entity.address,
        role=entity.role,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )

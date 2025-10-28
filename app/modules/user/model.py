from sqlalchemy import Column, String, Boolean, DateTime, UUID, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    fullname = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(String(128), nullable=True)
    role = Column(String(128), nullable=False, default='USER')
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert to dict for JSON response"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "fullname": self.fullname,
            "phone_number": self.phone_number,
            "gender": self.gender,
            "address": self.address,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
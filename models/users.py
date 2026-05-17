from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime, nullable=True)
    added_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=True, default=datetime.utcnow)

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT

from database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    description = Column(LONGTEXT, nullable=True)
    added_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)
    deleted_date = Column(DateTime, nullable=True)

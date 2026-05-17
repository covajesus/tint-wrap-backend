from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT

from database import Base


class ServiceGallery(Base):
    __tablename__ = "service_galleries"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    gallery_type_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    file1 = Column(LONGTEXT, nullable=True)
    file2 = Column(LONGTEXT, nullable=True)
    added_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)
    deleted_date = Column(DateTime, nullable=True)

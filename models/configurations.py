from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    site_title = Column(String(255), nullable=False, default="TintWrap")
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    youtube_url = Column(String(512), nullable=True)
    tiktok_url = Column(String(512), nullable=True)
    instagram_url = Column(String(512), nullable=True)
    facebook_url = Column(String(512), nullable=True)
    phone = Column(String(64), nullable=True)
    contact_email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    whatsapp_url = Column(String(512), nullable=True)
    added_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)

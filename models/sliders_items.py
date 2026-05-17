from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database import Base


class SliderItem(Base):
    __tablename__ = "slider_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    slider_id = Column(Integer, ForeignKey("sliders.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    photo_video = Column(String(255), nullable=True)
    added_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_date = Column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

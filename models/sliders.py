from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base

# 1 = visible en el sitio (convención del proyecto)
ACTIVE_STATUS_VISIBLE = 1


class Slider(Base):
    __tablename__ = "sliders"

    id = Column(Integer, primary_key=True, index=True)
    active_status_id = Column(Integer, nullable=False, default=ACTIVE_STATUS_VISIBLE)
    slider = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    added_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_date = Column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_date = Column(DateTime, nullable=True)

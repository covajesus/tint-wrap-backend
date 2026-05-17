from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from database import Base


class Slider(Base):
    __tablename__ = "sliders"

    id = Column(Integer, primary_key=True, index=True)
    main_title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    slider_image_video = Column(Text, nullable=True)
    main_button_text = Column(String(100), nullable=True)
    main_button_url = Column(String(255), nullable=True)
    second_button_textt = Column(String(100), nullable=True)
    second_button_url = Column(String(255), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    active = Column(Boolean, nullable=False, default=True)
    added_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_date = Column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_date = Column(DateTime, nullable=True)

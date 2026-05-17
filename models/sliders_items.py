from sqlalchemy import Column, ForeignKey, Integer, String, Text

from database import Base


class SliderItem(Base):
    __tablename__ = "sliders_items"

    id = Column(Integer, primary_key=True, index=True)
    slideer_id = Column(Integer, ForeignKey("sliders.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    photo_video = Column(Text, nullable=True)

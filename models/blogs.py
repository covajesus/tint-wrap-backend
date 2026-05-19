from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    extract = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    added_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_date = Column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

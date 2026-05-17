from sqlalchemy import Column, Integer, String, Text

from database import Base


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    extract = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    image = Column(Text, nullable=True)

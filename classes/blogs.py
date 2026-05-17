from sqlalchemy.orm import Session

from models.blogs import Blog
from schemas.blogs import CreateBlog, UpdateBlog


class BlogClass:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Blog]:
        return (
            self.db.query(Blog)
            .order_by(Blog.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, blog_id: int) -> Blog | None:
        return self.db.query(Blog).filter(Blog.id == blog_id).first()

    def store(self, blog: CreateBlog) -> Blog:
        data = blog.model_dump(exclude_none=True)
        db_blog = Blog(**data)

        self.db.add(db_blog)
        self.db.commit()
        self.db.refresh(db_blog)

        return db_blog

    def update(self, blog_id: int, blog: UpdateBlog) -> Blog | None:
        db_blog = self.get_by_id(blog_id)

        if db_blog is None:
            return None

        data = blog.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(db_blog, field, value)

        self.db.commit()
        self.db.refresh(db_blog)

        return db_blog

    def delete(self, blog_id: int) -> bool:
        db_blog = self.get_by_id(blog_id)

        if db_blog is None:
            return False

        self.db.delete(db_blog)
        self.db.commit()

        return True

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from classes.blogs import BlogClass
from database import get_db
from dependencies.auth import get_current_user
from schemas.blogs import BlogSchema, CreateBlog, UpdateBlog


router = APIRouter(prefix="/api/blogs", tags=["Blogs"])


@router.get("/", response_model=list[BlogSchema])
def index(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[BlogSchema]:
    return BlogClass(db).get_all(skip=skip, limit=limit)


@router.get("/{blog_id}", response_model=BlogSchema)
def show(blog_id: int, db: Session = Depends(get_db)) -> BlogSchema:
    blog = BlogClass(db).get_by_id(blog_id)

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    return blog


@router.post(
    "/",
    response_model=BlogSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def store(
    blog: CreateBlog,
    db: Session = Depends(get_db),
) -> BlogSchema:
    return BlogClass(db).store(blog)


@router.put(
    "/{blog_id}",
    response_model=BlogSchema,
    dependencies=[Depends(get_current_user)],
)
@router.patch(
    "/{blog_id}",
    response_model=BlogSchema,
    dependencies=[Depends(get_current_user)],
)
def update(
    blog_id: int,
    blog: UpdateBlog,
    db: Session = Depends(get_db),
) -> BlogSchema:
    updated_blog = BlogClass(db).update(blog_id, blog)

    if updated_blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    return updated_blog


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def destroy(blog_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    deleted = BlogClass(db).delete(blog_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    return {"message": "Blog deleted successfully"}

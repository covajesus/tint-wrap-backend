from pydantic import BaseModel, ConfigDict, Field


class CreateBlog(BaseModel):
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    extract: str | None = None
    content: str | None = None
    image: str | None = None


class UpdateBlog(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    extract: str | None = None
    content: str | None = None
    image: str | None = None


class BlogSchema(BaseModel):
    id: int
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    extract: str | None = None
    content: str | None = None
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)

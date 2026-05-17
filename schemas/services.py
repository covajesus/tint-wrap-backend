from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.service_galleries import ServiceGallerySchema


class CreateServiceGalleryNested(BaseModel):
    gallery_type_id: int
    title: str | None = None
    file1: str | None = None
    file2: str | None = None


class UpdateServiceGalleryNested(BaseModel):
    id: int | None = None
    gallery_type_id: int | None = None
    title: str | None = None
    file1: str | None = None
    file2: str | None = None


class CreateService(BaseModel):
    title: str = Field(..., max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    description: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None
    galleries: list[CreateServiceGalleryNested] = []


class UpdateService(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    description: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None
    deleted_date: datetime | None = None
    galleries: list[UpdateServiceGalleryNested] | None = None


class ServiceSchema(BaseModel):
    id: int
    title: str = Field(..., max_length=255)
    subtitle: str | None = None
    description: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None
    deleted_date: datetime | None = None
    galleries: list[ServiceGallerySchema] = []

    model_config = ConfigDict(from_attributes=True)

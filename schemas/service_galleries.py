from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateServiceGallery(BaseModel):
    service_id: int
    gallery_type_id: int
    title: str | None = None
    file1: str | None = None
    file2: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None


class UpdateServiceGallery(BaseModel):
    service_id: int | None = None
    gallery_type_id: int | None = None
    title: str | None = None
    file1: str | None = None
    file2: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None
    deleted_date: datetime | None = None


class ServiceGallerySchema(BaseModel):
    id: int
    service_id: int
    gallery_type_id: int
    title: str | None = None
    file1: str | None = None
    file2: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None
    deleted_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

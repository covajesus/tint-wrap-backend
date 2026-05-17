from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateSliderItem(BaseModel):
    slider_id: int
    title: str = Field(..., max_length=255)
    photo_video: str | None = Field(default=None, max_length=255)
    added_date: datetime | None = None
    updated_date: datetime | None = None


class UpdateSliderItem(BaseModel):
    slider_id: int | None = None
    title: str | None = Field(default=None, max_length=255)
    photo_video: str | None = Field(default=None, max_length=255)
    added_date: datetime | None = None
    updated_date: datetime | None = None


class SliderItemSchema(BaseModel):
    id: int
    slider_id: int
    title: str = Field(..., max_length=255)
    photo_video: str | None = Field(default=None, max_length=255)
    added_date: datetime | None = None
    updated_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

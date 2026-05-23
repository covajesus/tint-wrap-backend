from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

ACTIVE_STATUS_VISIBLE = 1


class CreateSlider(BaseModel):
    slider: str | None = None
    url: str | None = Field(default=None, max_length=500)
    order: int = 0
    active_status_id: int = ACTIVE_STATUS_VISIBLE
    added_date: datetime | None = None
    updated_date: datetime | None = None


class UpdateSlider(BaseModel):
    slider: str | None = None
    url: str | None = Field(default=None, max_length=500)
    order: int | None = None
    active_status_id: int | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None


class SliderSchema(BaseModel):
    id: int
    active_status_id: int = ACTIVE_STATUS_VISIBLE
    slider: str | None = None
    url: str | None = Field(default=None, max_length=500)
    order: int = 0
    added_date: datetime | None = None
    updated_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

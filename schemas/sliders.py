from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateSlider(BaseModel):
    main_title: str = Field(..., max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    slider_image_video: str | None = None
    main_button_text: str | None = Field(default=None, max_length=100)
    main_button_url: str | None = Field(default=None, max_length=255)
    second_button_textt: str | None = Field(default=None, max_length=100)
    second_button_url: str | None = Field(default=None, max_length=255)
    order: int = 0
    active: bool = True
    added_date: datetime | None = None
    updated_date: datetime | None = None


class UpdateSlider(BaseModel):
    main_title: str | None = Field(default=None, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    slider_image_video: str | None = None
    main_button_text: str | None = Field(default=None, max_length=100)
    main_button_url: str | None = Field(default=None, max_length=255)
    second_button_textt: str | None = Field(default=None, max_length=100)
    second_button_url: str | None = Field(default=None, max_length=255)
    order: int | None = None
    active: bool | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None


class SliderSchema(BaseModel):
    id: int
    main_title: str = Field(..., max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    slider_image_video: str | None = None
    main_button_text: str | None = Field(default=None, max_length=100)
    main_button_url: str | None = Field(default=None, max_length=255)
    second_button_textt: str | None = Field(default=None, max_length=100)
    second_button_url: str | None = Field(default=None, max_length=255)
    order: int = 0
    active: bool = True
    added_date: datetime | None = None
    updated_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

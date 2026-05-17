from pydantic import BaseModel, ConfigDict, Field


class CreateSliderItem(BaseModel):
    slideer_id: int
    title: str = Field(..., max_length=255)
    photo_video: str | None = None


class UpdateSliderItem(BaseModel):
    slideer_id: int | None = None
    title: str | None = Field(default=None, max_length=255)
    photo_video: str | None = None


class SliderItemSchema(BaseModel):
    id: int
    slideer_id: int
    title: str = Field(..., max_length=255)
    photo_video: str | None = None

    model_config = ConfigDict(from_attributes=True)

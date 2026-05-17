from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UpdateConfiguration(BaseModel):
    site_title: str | None = Field(default=None, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = None
    youtube_url: str | None = Field(default=None, max_length=512)
    tiktok_url: str | None = Field(default=None, max_length=512)
    instagram_url: str | None = Field(default=None, max_length=512)
    facebook_url: str | None = Field(default=None, max_length=512)
    phone: str | None = Field(default=None, max_length=64)
    contact_email: str | None = Field(default=None, max_length=255)
    address: str | None = None
    whatsapp_url: str | None = Field(default=None, max_length=512)


class ConfigurationSchema(BaseModel):
    id: int
    site_title: str
    meta_title: str | None = None
    meta_description: str | None = None
    youtube_url: str | None = None
    tiktok_url: str | None = None
    instagram_url: str | None = None
    facebook_url: str | None = None
    phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    whatsapp_url: str | None = None
    added_date: datetime | None = None
    updated_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime

from sqlalchemy.orm import Session

from models.configurations import Configuration
from schemas.configurations import (
    ConfigurationSchema,
    UpdateConfiguration,
    VisitorCountSchema,
)
from utils.tiktok_feed import invalidate_tiktok_cache
from utils.youtube_feed import invalidate_youtube_cache

DEFAULT_CONFIGURATION_ID = 1


class ConfigurationClass:
    def __init__(self, db: Session):
        self.db = db

    def _default_row(self) -> Configuration:
        now = datetime.utcnow()
        return Configuration(
            id=DEFAULT_CONFIGURATION_ID,
            site_title="TintWrap",
            meta_title="",
            meta_description="",
            youtube_url="",
            tiktok_url="",
            instagram_url="",
            facebook_url="",
            phone="",
            contact_email="",
            address="",
            whatsapp_url="https://wa.me/",
            visitior=0,
            added_date=now,
            updated_date=now,
        )

    def _get_or_create_row(self) -> Configuration:
        row = (
            self.db.query(Configuration)
            .filter(Configuration.id == DEFAULT_CONFIGURATION_ID)
            .first()
        )
        if row is None:
            row = self._default_row()
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
        return row

    def get_visitior_count(self) -> VisitorCountSchema:
        row = self._get_or_create_row()
        return VisitorCountSchema(visitior=int(row.visitior or 0))

    def increment_visitior(self) -> VisitorCountSchema:
        row = self._get_or_create_row()
        row.visitior = int(row.visitior or 0) + 1
        row.updated_date = datetime.utcnow()
        if row.added_date is None:
            row.added_date = row.updated_date
        self.db.commit()
        self.db.refresh(row)
        return VisitorCountSchema(visitior=int(row.visitior or 0))

    def get_singleton(self) -> ConfigurationSchema:
        row = self._get_or_create_row()
        return ConfigurationSchema.model_validate(row)

    def update_singleton(self, payload: UpdateConfiguration) -> ConfigurationSchema:
        row = self._get_or_create_row()

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(row, field, value)

        row.updated_date = datetime.utcnow()
        if row.added_date is None:
            row.added_date = row.updated_date

        self.db.commit()
        self.db.refresh(row)

        if "tiktok_url" in data:
            invalidate_tiktok_cache()
        if "youtube_url" in data:
            invalidate_youtube_cache()

        return ConfigurationSchema.model_validate(row)

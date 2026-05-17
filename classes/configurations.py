from datetime import datetime

from sqlalchemy.orm import Session

from models.configurations import Configuration
from schemas.configurations import ConfigurationSchema, UpdateConfiguration

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
            added_date=now,
            updated_date=now,
        )

    def get_singleton(self) -> ConfigurationSchema:
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

        return ConfigurationSchema.model_validate(row)

    def update_singleton(self, payload: UpdateConfiguration) -> ConfigurationSchema:
        row = (
            self.db.query(Configuration)
            .filter(Configuration.id == DEFAULT_CONFIGURATION_ID)
            .first()
        )

        if row is None:
            row = self._default_row()
            self.db.add(row)
            self.db.flush()

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(row, field, value)

        row.updated_date = datetime.utcnow()
        if row.added_date is None:
            row.added_date = row.updated_date

        self.db.commit()
        self.db.refresh(row)

        return ConfigurationSchema.model_validate(row)

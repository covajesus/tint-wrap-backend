from datetime import datetime

from sqlalchemy.orm import Session

from models.sliders import Slider
from schemas.sliders import CreateSlider, UpdateSlider
from utils.datetime_coerce import parse_db_datetime
from utils.media_storage import delete_slider_upload_folder, persist_slider_media

_DATE_FIELDS = ("added_date", "updated_date", "deleted_date")


class SliderClass:
    def __init__(self, db: Session):
        self.db = db

    def _active_query(self):
        return self.db.query(Slider).filter(Slider.deleted_date.is_(None))

    @staticmethod
    def _normalize_dates(slider: Slider) -> Slider:
        for field in _DATE_FIELDS:
            value = getattr(slider, field, None)
            if isinstance(value, str):
                setattr(slider, field, parse_db_datetime(value))
        return slider

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Slider]:
        rows = (
            self._active_query()
            .order_by(Slider.order.asc(), Slider.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._normalize_dates(row) for row in rows]

    def get_by_id(self, slider_id: int) -> Slider | None:
        slider = self._active_query().filter(Slider.id == slider_id).first()
        if slider is None:
            return None
        return self._normalize_dates(slider)

    def store(self, slider: CreateSlider) -> Slider:
        now = datetime.utcnow()
        data = slider.model_dump(exclude_none=True)
        media = data.pop("slider_image_video", None)

        if "added_date" not in data:
            data["added_date"] = now
        if "updated_date" not in data:
            data["updated_date"] = now

        try:
            db_slider = Slider(**data)
            self.db.add(db_slider)
            self.db.flush()

            if media is not None and str(media).strip():
                db_slider.slider_image_video = persist_slider_media(
                    media,
                    slider_id=db_slider.id,
                )

            self.db.commit()
            self.db.refresh(db_slider)
            return db_slider
        except Exception:
            self.db.rollback()
            raise

    def update(self, slider_id: int, slider: UpdateSlider) -> Slider | None:
        db_slider = self.get_by_id(slider_id)

        if db_slider is None:
            return None

        data = slider.model_dump(exclude_unset=True)
        media = data.pop("slider_image_video", None)

        for field, value in data.items():
            setattr(db_slider, field, value)

        if media is not None:
            db_slider.slider_image_video = persist_slider_media(
                media,
                slider_id=slider_id,
                previous=db_slider.slider_image_video,
            )

        db_slider.updated_date = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(db_slider)
            return db_slider
        except Exception:
            self.db.rollback()
            raise

    def delete(self, slider_id: int) -> bool:
        db_slider = self.get_by_id(slider_id)

        if db_slider is None:
            return False

        db_slider.deleted_date = datetime.utcnow()
        self.db.commit()
        delete_slider_upload_folder(slider_id)

        return True

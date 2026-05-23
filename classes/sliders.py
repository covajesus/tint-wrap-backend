from datetime import datetime

from sqlalchemy.orm import Session

from models.sliders import Slider
from schemas.sliders import CreateSlider, UpdateSlider
from utils.media_storage import delete_slider_upload_folder, persist_slider_media


class SliderClass:
    def __init__(self, db: Session):
        self.db = db

    def _active_query(self):
        return self.db.query(Slider).filter(Slider.deleted_date.is_(None))

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Slider]:
        return (
            self._active_query()
            .order_by(Slider.order.asc(), Slider.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, slider_id: int) -> Slider | None:
        return self._active_query().filter(Slider.id == slider_id).first()

    def _reindex_orders(self) -> None:
        """Renumera order a 1..n entre sliders activos (sin huecos)."""
        sliders = (
            self._active_query()
            .order_by(Slider.order.asc(), Slider.id.asc())
            .all()
        )
        now = datetime.utcnow()
        for index, slider in enumerate(sliders):
            new_order = index + 1
            if slider.order != new_order:
                slider.order = new_order
                slider.updated_date = now

    def store(self, slider: CreateSlider) -> Slider:
        now = datetime.utcnow()
        data = slider.model_dump(exclude_none=True)
        media = data.pop("slider", None)

        if "added_date" not in data:
            data["added_date"] = now
        if "updated_date" not in data:
            data["updated_date"] = now

        try:
            db_slider = Slider(**data)
            self.db.add(db_slider)
            self.db.flush()

            if media is not None and str(media).strip():
                db_slider.slider = persist_slider_media(
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
        media = data.pop("slider", None)

        for field, value in data.items():
            setattr(db_slider, field, value)

        if media is not None:
            db_slider.slider = persist_slider_media(
                media,
                slider_id=slider_id,
                previous=db_slider.slider,
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

        try:
            db_slider.deleted_date = datetime.utcnow()
            self.db.flush()
            self._reindex_orders()
            self.db.commit()
            delete_slider_upload_folder(slider_id)
            return True
        except Exception:
            self.db.rollback()
            raise

from sqlalchemy.orm import Session

from models.sliders_items import SliderItem
from schemas.sliders_items import CreateSliderItem, UpdateSliderItem


class SliderItemClass:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[SliderItem]:
        return (
            self.db.query(SliderItem)
            .order_by(SliderItem.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, slider_item_id: int) -> SliderItem | None:
        return (
            self.db.query(SliderItem)
            .filter(SliderItem.id == slider_item_id)
            .first()
        )

    def store(self, slider_item: CreateSliderItem) -> SliderItem:
        data = slider_item.model_dump(exclude_none=True)
        db_slider_item = SliderItem(**data)

        self.db.add(db_slider_item)
        self.db.commit()
        self.db.refresh(db_slider_item)

        return db_slider_item

    def update(
        self,
        slider_item_id: int,
        slider_item: UpdateSliderItem,
    ) -> SliderItem | None:
        db_slider_item = self.get_by_id(slider_item_id)

        if db_slider_item is None:
            return None

        data = slider_item.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(db_slider_item, field, value)

        self.db.commit()
        self.db.refresh(db_slider_item)

        return db_slider_item

    def delete(self, slider_item_id: int) -> bool:
        db_slider_item = self.get_by_id(slider_item_id)

        if db_slider_item is None:
            return False

        self.db.delete(db_slider_item)
        self.db.commit()

        return True

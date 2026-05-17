from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from classes.sliders_items import SliderItemClass
from database import get_db
from schemas.sliders_items import (
    CreateSliderItem,
    SliderItemSchema,
    UpdateSliderItem,
)


router = APIRouter(prefix="/api/sliders-items", tags=["Sliders Items"])


@router.get("/", response_model=list[SliderItemSchema])
def index(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[SliderItemSchema]:
    return SliderItemClass(db).get_all(skip=skip, limit=limit)


@router.get("/{slider_item_id}", response_model=SliderItemSchema)
def show(
    slider_item_id: int,
    db: Session = Depends(get_db),
) -> SliderItemSchema:
    slider_item = SliderItemClass(db).get_by_id(slider_item_id)

    if slider_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider item not found",
        )

    return slider_item


@router.post(
    "/",
    response_model=SliderItemSchema,
    status_code=status.HTTP_201_CREATED,
)
def store(
    slider_item: CreateSliderItem,
    db: Session = Depends(get_db),
) -> SliderItemSchema:
    return SliderItemClass(db).store(slider_item)


@router.put("/{slider_item_id}", response_model=SliderItemSchema)
@router.patch("/{slider_item_id}", response_model=SliderItemSchema)
def update(
    slider_item_id: int,
    slider_item: UpdateSliderItem,
    db: Session = Depends(get_db),
) -> SliderItemSchema:
    updated_slider_item = SliderItemClass(db).update(slider_item_id, slider_item)

    if updated_slider_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider item not found",
        )

    return updated_slider_item


@router.delete("/{slider_item_id}", status_code=status.HTTP_200_OK)
def destroy(
    slider_item_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    deleted = SliderItemClass(db).delete(slider_item_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider item not found",
        )

    return {"message": "Slider item deleted successfully"}

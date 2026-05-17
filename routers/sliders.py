from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from classes.sliders import SliderClass
from database import get_db
from dependencies.auth import get_current_user
from schemas.sliders import CreateSlider, SliderSchema, UpdateSlider


router = APIRouter(prefix="/api/sliders", tags=["Sliders"])


@router.get("/", response_model=list[SliderSchema])
def index(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[SliderSchema]:
    try:
        return SliderClass(db).get_all(skip=skip, limit=limit)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Error al leer sliders: {exc}. "
                "Reinicia el backend (python -m uvicorn main:app --port 8030) "
                "tras actualizar el código."
            ),
        ) from exc


@router.get("/{slider_id}", response_model=SliderSchema)
def show(slider_id: int, db: Session = Depends(get_db)) -> SliderSchema:
    slider = SliderClass(db).get_by_id(slider_id)

    if slider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider not found",
        )

    return slider


@router.post(
    "/",
    response_model=SliderSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def store(
    slider: CreateSlider,
    db: Session = Depends(get_db),
) -> SliderSchema:
    return SliderClass(db).store(slider)


@router.put(
    "/{slider_id}",
    response_model=SliderSchema,
    dependencies=[Depends(get_current_user)],
)
@router.patch(
    "/{slider_id}",
    response_model=SliderSchema,
    dependencies=[Depends(get_current_user)],
)
def update(
    slider_id: int,
    slider: UpdateSlider,
    db: Session = Depends(get_db),
) -> SliderSchema:
    updated_slider = SliderClass(db).update(slider_id, slider)

    if updated_slider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider not found",
        )

    return updated_slider


@router.delete(
    "/{slider_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def destroy(slider_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    deleted = SliderClass(db).delete(slider_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slider not found",
        )

    return {"message": "Slider deleted successfully"}

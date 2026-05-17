from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from classes.service_galleries import ServiceGalleryClass
from database import get_db
from dependencies.auth import get_current_user
from schemas.service_galleries import (
    CreateServiceGallery,
    ServiceGallerySchema,
    UpdateServiceGallery,
)


router = APIRouter(prefix="/api/service-galleries", tags=["Service Galleries"])


@router.get("/", response_model=list[ServiceGallerySchema])
def index(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ServiceGallerySchema]:
    return ServiceGalleryClass(db).get_all(skip=skip, limit=limit)


@router.get("/service/{service_id}", response_model=list[ServiceGallerySchema])
def index_by_service(
    service_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ServiceGallerySchema]:
    return ServiceGalleryClass(db).get_by_service_id(
        service_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{gallery_id}", response_model=ServiceGallerySchema)
def show(
    gallery_id: int,
    db: Session = Depends(get_db),
) -> ServiceGallerySchema:
    gallery = ServiceGalleryClass(db).get_by_id(gallery_id)

    if gallery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service gallery not found",
        )

    return gallery


@router.post(
    "/",
    response_model=ServiceGallerySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def store(
    gallery: CreateServiceGallery,
    db: Session = Depends(get_db),
) -> ServiceGallerySchema:
    return ServiceGalleryClass(db).store(gallery)


@router.put(
    "/{gallery_id}",
    response_model=ServiceGallerySchema,
    dependencies=[Depends(get_current_user)],
)
@router.patch(
    "/{gallery_id}",
    response_model=ServiceGallerySchema,
    dependencies=[Depends(get_current_user)],
)
def update(
    gallery_id: int,
    gallery: UpdateServiceGallery,
    db: Session = Depends(get_db),
) -> ServiceGallerySchema:
    updated_gallery = ServiceGalleryClass(db).update(gallery_id, gallery)

    if updated_gallery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service gallery not found",
        )

    return updated_gallery


@router.delete(
    "/{gallery_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def destroy(
    gallery_id: int,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    deleted = ServiceGalleryClass(db).delete(gallery_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service gallery not found",
        )

    return {"message": "Service gallery deleted successfully"}

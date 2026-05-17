from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from classes.services import ServiceClass
from database import get_db
from schemas.services import CreateService, ServiceSchema, UpdateService


router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("/", response_model=list[ServiceSchema])
def index(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ServiceSchema]:
    return ServiceClass(db).get_all(skip=skip, limit=limit)


@router.get("/{service_id}", response_model=ServiceSchema)
def show(service_id: int, db: Session = Depends(get_db)) -> ServiceSchema:
    service = ServiceClass(db).get_by_id(service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service


@router.post(
    "/",
    response_model=ServiceSchema,
    status_code=status.HTTP_201_CREATED,
)
def store(
    service: CreateService,
    db: Session = Depends(get_db),
) -> ServiceSchema:
    return ServiceClass(db).store(service)


@router.put("/{service_id}", response_model=ServiceSchema)
@router.patch("/{service_id}", response_model=ServiceSchema)
def update(
    service_id: int,
    service: UpdateService,
    db: Session = Depends(get_db),
) -> ServiceSchema:
    updated_service = ServiceClass(db).update(service_id, service)

    if updated_service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return updated_service


@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def destroy(service_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    deleted = ServiceClass(db).delete(service_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return {"message": "Service deleted successfully"}

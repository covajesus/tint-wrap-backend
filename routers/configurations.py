from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from classes.configurations import ConfigurationClass
from database import get_db
from dependencies.auth import get_current_user
from schemas.configurations import ConfigurationSchema, UpdateConfiguration


router = APIRouter(prefix="/api/configuration", tags=["Configuration"])


@router.get("/", response_model=ConfigurationSchema)
def show(db: Session = Depends(get_db)) -> ConfigurationSchema:
    return ConfigurationClass(db).get_singleton()


@router.put(
    "/",
    response_model=ConfigurationSchema,
    dependencies=[Depends(get_current_user)],
)
def update(
    payload: UpdateConfiguration,
    db: Session = Depends(get_db),
) -> ConfigurationSchema:
    return ConfigurationClass(db).update_singleton(payload)

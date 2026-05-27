from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from classes.configurations import ConfigurationClass
from database import get_db
from schemas.configurations import VisitorCountSchema

router = APIRouter(prefix="/api/visitors", tags=["Visitors"])


@router.get("/", response_model=VisitorCountSchema)
def get_visitor_count(db: Session = Depends(get_db)) -> VisitorCountSchema:
    """Devuelve el total de visitantes sin incrementar."""
    return ConfigurationClass(db).get_visitior_count()


@router.post("/", response_model=VisitorCountSchema)
def register_visit(db: Session = Depends(get_db)) -> VisitorCountSchema:
    """Suma 1 al contador visitior en configurations (id=1)."""
    return ConfigurationClass(db).increment_visitior()

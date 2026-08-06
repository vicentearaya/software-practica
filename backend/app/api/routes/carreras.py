from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.carrera import Carrera
from app.schemas.carrera import CarreraOut

router = APIRouter(prefix="/carreras", tags=["carreras"])


@router.get("", response_model=list[CarreraOut])
def listar_carreras(db: Session = Depends(get_db)) -> list[Carrera]:
    """Catálogo de carreras, público: alimenta el selector del registro de estudiantes.

    Crear carreras es exclusivo del administrador y se implementa en su rama.
    """
    return list(db.scalars(select(Carrera).order_by(Carrera.nombre)).all())

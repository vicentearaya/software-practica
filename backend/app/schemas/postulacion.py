from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ModalidadOferta
from app.models.postulacion import MAX_CARTA_PRESENTACION
from app.schemas.carrera import CarreraOut


class OfertaEstudianteOut(BaseModel):
    """Oferta visible para el estudiante (aprobada y de su carrera)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descripcion: str
    requisitos: str
    modalidad: ModalidadOferta
    calle: str | None = None
    numero: str | None = None
    comuna: str | None = None
    region: str | None = None
    creado_en: datetime
    carrera: CarreraOut
    empresa: str


class PostularRequest(BaseModel):
    carta_presentacion: str = Field(min_length=1, max_length=MAX_CARTA_PRESENTACION)


class PostulacionOut(BaseModel):
    """Postulación del estudiante con los datos de la oferta."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    carta_presentacion: str
    creado_en: datetime
    oferta: OfertaEstudianteOut

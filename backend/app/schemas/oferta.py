from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import EstadoOferta, ModalidadOferta
from app.schemas.carrera import CarreraOut


class EmpleadorResumenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa: str
    nombre: str
    apellido: str
    correo: EmailStr


class EstudianteInscritoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    postulacion_id: int
    nombre: str
    apellido: str
    correo: EmailStr
    carrera: str
    carta_presentacion: str


class OfertaAdminOut(BaseModel):
    """Oferta con toda su información y los estudiantes inscritos."""

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
    estado: EstadoOferta
    motivo_rechazo: str | None = None
    creado_en: datetime
    carrera: CarreraOut
    empleador: EmpleadorResumenOut
    estudiantes: list[EstudianteInscritoOut]


class RechazarOfertaRequest(BaseModel):
    motivo: str = Field(min_length=1, max_length=2000)

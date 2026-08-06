from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

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


class OfertaCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str = Field(min_length=1)
    requisitos: str = Field(min_length=1)
    carrera_id: int
    modalidad: ModalidadOferta
    calle: str | None = Field(default=None, max_length=150)
    numero: str | None = Field(default=None, max_length=20)
    comuna: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validar_direccion_segun_modalidad(self) -> "OfertaCreate":
        # Remoto: sin dirección. Presencial/híbrida: dirección obligatoria.
        if self.modalidad == ModalidadOferta.REMOTO:
            if any([self.calle, self.numero, self.comuna, self.region]):
                raise ValueError("Una oferta remota no debe incluir dirección")
            return self

        faltantes = [
            campo
            for campo, valor in (
                ("calle", self.calle),
                ("numero", self.numero),
                ("comuna", self.comuna),
                ("region", self.region),
            )
            if not (valor and valor.strip())
        ]
        if faltantes:
            raise ValueError(
                "La dirección (calle, número, comuna y región) es obligatoria "
                "si la modalidad es presencial o híbrida"
            )
        self.calle = self.calle.strip()  # type: ignore[union-attr]
        self.numero = self.numero.strip()  # type: ignore[union-attr]
        self.comuna = self.comuna.strip()  # type: ignore[union-attr]
        self.region = self.region.strip()  # type: ignore[union-attr]
        return self


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


class OfertaEmpleadorOut(BaseModel):
    """Oferta del empleador, con postulantes cuando está aprobada."""

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
    cantidad_postulantes: int
    estudiantes: list[EstudianteInscritoOut]


class RechazarOfertaRequest(BaseModel):
    motivo: str = Field(min_length=1, max_length=2000)

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import RolUsuario


class RegistroBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=72)


class RegistroEstudiante(RegistroBase):
    # El tipo de usuario es lo primero que se pide en el formulario de registro.
    tipo: Literal["estudiante"]
    carrera_id: int


class RegistroEmpleador(RegistroBase):
    tipo: Literal["empleador"]
    empresa: str = Field(min_length=1, max_length=150)


# El administrador no es un tipo registrable: no existe variante para "admin",
# así que cualquier intento de registrarse como admin falla en la validación.
RegistroRequest = Annotated[
    Union[RegistroEstudiante, RegistroEmpleador],
    Field(discriminator="tipo"),
]


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    correo: EmailStr
    rol: RolUsuario


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut

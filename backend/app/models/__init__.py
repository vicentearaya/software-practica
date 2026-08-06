"""Modelos de la base de datos.

Se importan todos aquí para que `Base.metadata` esté completo cuando lo usen
Alembic y la aplicación.
"""

from app.models.carrera import Carrera
from app.models.empleador import Empleador
from app.models.enums import EstadoOferta, ModalidadOferta, RolUsuario
from app.models.estudiante import Estudiante
from app.models.oferta import Oferta
from app.models.postulacion import Postulacion
from app.models.usuario import Usuario

__all__ = [
    "Carrera",
    "Empleador",
    "Estudiante",
    "EstadoOferta",
    "ModalidadOferta",
    "Oferta",
    "Postulacion",
    "RolUsuario",
    "Usuario",
]

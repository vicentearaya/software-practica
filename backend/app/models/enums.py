import enum


class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    EMPLEADOR = "empleador"
    ESTUDIANTE = "estudiante"


class ModalidadOferta(str, enum.Enum):
    REMOTO = "remoto"
    PRESENCIAL = "presencial"
    HIBRIDA = "hibrida"


class EstadoOferta(str, enum.Enum):
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


# Nombres de los tipos ENUM en PostgreSQL (usados también por la migración).
NOMBRE_ENUM_ROL = "rol_usuario"
NOMBRE_ENUM_MODALIDAD = "modalidad_oferta"
NOMBRE_ENUM_ESTADO = "estado_oferta"

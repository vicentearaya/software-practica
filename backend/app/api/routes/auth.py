from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_actual
from app.core.seguridad import crear_token, hashear_password, verificar_password
from app.db.session import get_db
from app.models.carrera import Carrera
from app.models.empleador import Empleador
from app.models.enums import RolUsuario
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.schemas.auth import (
    LoginRequest,
    RegistroEmpleador,
    RegistroEstudiante,
    RegistroRequest,
    TokenOut,
    UsuarioOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _usuario_out(usuario: Usuario) -> UsuarioOut:
    """Serializa el usuario e incluye empresa cuando el rol es empleador."""
    return UsuarioOut(
        id=usuario.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        rol=usuario.rol,
        empresa=usuario.empleador.empresa if usuario.empleador is not None else None,
    )


@router.post("/registro", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def registrar(datos: RegistroRequest, db: Session = Depends(get_db)) -> TokenOut:
    """Registra un estudiante o un empleador. El administrador no es registrable."""
    correo = datos.correo.lower()
    existe = db.scalar(select(Usuario).where(Usuario.correo == correo))
    if existe is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo",
        )

    if isinstance(datos, RegistroEstudiante):
        carrera = db.get(Carrera, datos.carrera_id)
        if carrera is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La carrera indicada no existe",
            )
        rol = RolUsuario.ESTUDIANTE
    else:
        rol = RolUsuario.EMPLEADOR

    usuario = Usuario(
        nombre=datos.nombre.strip(),
        apellido=datos.apellido.strip(),
        correo=correo,
        password_hash=hashear_password(datos.password),
        rol=rol,
    )
    db.add(usuario)
    db.flush()  # necesitamos el id del usuario para el perfil

    if isinstance(datos, RegistroEstudiante):
        db.add(Estudiante(usuario_id=usuario.id, carrera_id=datos.carrera_id))
    elif isinstance(datos, RegistroEmpleador):
        db.add(Empleador(usuario_id=usuario.id, empresa=datos.empresa.strip()))

    db.commit()
    db.refresh(usuario)

    return TokenOut(
        access_token=crear_token(usuario.id, usuario.rol.value),
        usuario=_usuario_out(usuario),
    )


@router.post("/login", response_model=TokenOut)
def login(datos: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    usuario = db.scalar(select(Usuario).where(Usuario.correo == datos.correo.lower()))
    if usuario is None or not verificar_password(datos.password, usuario.password_hash):
        # Mismo mensaje para correo inexistente y contraseña incorrecta.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    return TokenOut(
        access_token=crear_token(usuario.id, usuario.rol.value),
        usuario=_usuario_out(usuario),
    )


@router.get("/yo", response_model=UsuarioOut)
def usuario_actual(usuario: Usuario = Depends(get_usuario_actual)) -> UsuarioOut:
    """Devuelve la sesión activa: el frontend la usa para saber a qué panel entrar."""
    return _usuario_out(usuario)

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.seguridad import decodificar_token
from app.db.session import get_db
from app.models.enums import RolUsuario
from app.models.usuario import Usuario

esquema_bearer = HTTPBearer(auto_error=False)

CREDENCIALES_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales inválidas o sesión expirada",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None:
        raise CREDENCIALES_INVALIDAS
    try:
        payload = decodificar_token(credenciales.credentials)
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise CREDENCIALES_INVALIDAS from exc

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise CREDENCIALES_INVALIDAS
    return usuario


def requiere_rol(*roles: RolUsuario):
    """Dependencia que exige uno de los roles indicados.

    La autorización se verifica siempre en el servidor: ocultar un botón en el
    navegador no es seguridad. Las ramas de cada rol usan esta dependencia.
    """

    def verificar(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para realizar esta acción",
            )
        return usuario

    return verificar

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import configuracion

# bcrypt solo considera los primeros 72 bytes de la contraseña; recortamos
# siempre igual al hashear y al verificar para que ambos coincidan.
LIMITE_BYTES_BCRYPT = 72


def _codificar(password: str) -> bytes:
    return password.encode("utf-8")[:LIMITE_BYTES_BCRYPT]


def hashear_password(password: str) -> str:
    return bcrypt.hashpw(_codificar(password), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_codificar(password), password_hash.encode("utf-8"))
    except ValueError:
        return False


def crear_token(usuario_id: int, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=configuracion.jwt_expiracion_minutos),
    }
    return jwt.encode(payload, configuracion.jwt_secret, algorithm=configuracion.jwt_algoritmo)


def decodificar_token(token: str) -> dict:
    """Devuelve el payload del token. Lanza jwt.PyJWTError si es inválido o expiró."""
    return jwt.decode(token, configuracion.jwt_secret, algorithms=[configuracion.jwt_algoritmo])

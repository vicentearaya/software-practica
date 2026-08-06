"""Datos de arranque: un administrador y las carreras iniciales.

Sin carreras ningún estudiante puede registrarse, porque el catálogo solo lo
crea el administrador. Es idempotente: se puede ejecutar en cada arranque.
"""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import configuracion
from app.core.seguridad import hashear_password
from app.db.session import SesionLocal
from app.models.carrera import Carrera
from app.models.enums import RolUsuario
from app.models.usuario import Usuario

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("seed")


def sembrar_admin(db: Session) -> None:
    correo = configuracion.seed_admin_correo.lower()
    if db.scalar(select(Usuario).where(Usuario.correo == correo)) is not None:
        log.info("Administrador ya existe (%s), no se toca.", correo)
        return

    db.add(
        Usuario(
            nombre=configuracion.seed_admin_nombre,
            apellido=configuracion.seed_admin_apellido,
            correo=correo,
            password_hash=hashear_password(configuracion.seed_admin_password),
            rol=RolUsuario.ADMIN,
        )
    )
    log.info("Administrador creado: %s", correo)


def sembrar_carreras(db: Session) -> None:
    existentes = set(db.scalars(select(Carrera.nombre)).all())
    nuevas = [n for n in configuracion.lista_seed_carreras if n not in existentes]
    db.add_all([Carrera(nombre=n) for n in nuevas])
    log.info("Carreras nuevas: %d (ya existían %d)", len(nuevas), len(existentes))


def main() -> None:
    with SesionLocal() as db:
        sembrar_admin(db)
        sembrar_carreras(db)
        db.commit()
    log.info("Seed completado.")


if __name__ == "__main__":
    main()

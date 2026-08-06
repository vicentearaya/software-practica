from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import NOMBRE_ENUM_ROL, RolUsuario


class Usuario(Base):
    """Cuenta de acceso. El rol define a qué panel entra la persona."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name=NOMBRE_ENUM_ROL, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    estudiante: Mapped["Estudiante | None"] = relationship(  # noqa: F821
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    empleador: Mapped["Empleador | None"] = relationship(  # noqa: F821
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )

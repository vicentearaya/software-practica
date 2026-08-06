from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Carrera(Base):
    """Catálogo de carreras. Solo el administrador las crea (rama de admin)."""

    __tablename__ = "carreras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

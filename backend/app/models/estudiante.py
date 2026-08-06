from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.carrera import Carrera
from app.models.usuario import Usuario


class Estudiante(Base):
    """Perfil de estudiante: usuario + carrera."""

    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # RESTRICT: una carrera con estudiantes inscritos no se puede borrar.
    carrera_id: Mapped[int] = mapped_column(
        ForeignKey("carreras.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    usuario: Mapped[Usuario] = relationship(back_populates="estudiante")
    carrera: Mapped[Carrera] = relationship()

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.usuario import Usuario


class Empleador(Base):
    """Perfil de empleador: usuario + empresa a la que pertenece."""

    __tablename__ = "empleadores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    empresa: Mapped[str] = mapped_column(String(150), nullable=False)

    usuario: Mapped[Usuario] = relationship(back_populates="empleador")

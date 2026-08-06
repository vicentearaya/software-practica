from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.estudiante import Estudiante
from app.models.oferta import Oferta

MAX_CARTA_PRESENTACION = 500


class Postulacion(Base):
    """Postulación de un estudiante a una oferta, con carta de presentación."""

    __tablename__ = "postulaciones"
    __table_args__ = (
        # Un estudiante no puede postular dos veces a la misma oferta:
        # la restricción vive en la base de datos, no solo en la interfaz.
        UniqueConstraint("estudiante_id", "oferta_id", name="uq_postulaciones_estudiante_oferta"),
        CheckConstraint(
            f"char_length(carta_presentacion) BETWEEN 1 AND {MAX_CARTA_PRESENTACION}",
            name="ck_postulaciones_largo_carta",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    oferta_id: Mapped[int] = mapped_column(
        ForeignKey("ofertas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    carta_presentacion: Mapped[str] = mapped_column(
        String(MAX_CARTA_PRESENTACION), nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    estudiante: Mapped[Estudiante] = relationship()
    oferta: Mapped[Oferta] = relationship()

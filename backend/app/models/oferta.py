from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.carrera import Carrera
from app.models.empleador import Empleador
from app.models.enums import (
    NOMBRE_ENUM_ESTADO,
    NOMBRE_ENUM_MODALIDAD,
    EstadoOferta,
    ModalidadOferta,
)

# El estado es la regla de negocio hecha dato: nace PENDIENTE, solo el
# administrador la mueve a APROBADA o a RECHAZADA (esta última con motivo).
CK_DIRECCION_SEGUN_MODALIDAD = (
    "(modalidad = 'remoto' AND calle IS NULL AND numero IS NULL "
    "AND comuna IS NULL AND region IS NULL) "
    "OR (modalidad IN ('presencial', 'hibrida') AND calle IS NOT NULL "
    "AND numero IS NOT NULL AND comuna IS NOT NULL AND region IS NOT NULL)"
)
CK_MOTIVO_RECHAZO = (
    "(estado = 'rechazada' AND motivo_rechazo IS NOT NULL) "
    "OR (estado <> 'rechazada' AND motivo_rechazo IS NULL)"
)


class Oferta(Base):
    """Oferta de práctica publicada por un empleador y revisada por el administrador."""

    __tablename__ = "ofertas"
    __table_args__ = (
        CheckConstraint(CK_DIRECCION_SEGUN_MODALIDAD, name="ck_ofertas_direccion_segun_modalidad"),
        CheckConstraint(CK_MOTIVO_RECHAZO, name="ck_ofertas_motivo_rechazo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empleador_id: Mapped[int] = mapped_column(
        ForeignKey("empleadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    requisitos: Mapped[str] = mapped_column(Text, nullable=False)
    # Una oferta apunta a una sola carrera.
    carrera_id: Mapped[int] = mapped_column(
        ForeignKey("carreras.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    modalidad: Mapped[ModalidadOferta] = mapped_column(
        Enum(
            ModalidadOferta,
            name=NOMBRE_ENUM_MODALIDAD,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )

    # Dirección: obligatoria solo si la modalidad es presencial o híbrida.
    calle: Mapped[str | None] = mapped_column(String(150), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    comuna: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estado: Mapped[EstadoOferta] = mapped_column(
        Enum(
            EstadoOferta,
            name=NOMBRE_ENUM_ESTADO,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default=EstadoOferta.PENDIENTE.value,
        index=True,
    )
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    empleador: Mapped[Empleador] = relationship()
    carrera: Mapped[Carrera] = relationship()
    postulaciones: Mapped[list["Postulacion"]] = relationship(  # noqa: F821
        back_populates="oferta", cascade="all, delete-orphan"
    )

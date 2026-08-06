"""Estructura inicial completa: usuarios, carreras, estudiantes, empleadores, ofertas, postulaciones.

Esta migración crea TODAS las tablas de la especificación con sus restricciones,
aunque ofertas y postulaciones todavía no tengan endpoints. Las ramas de cada rol
no deben crear migraciones nuevas.

Revision ID: 0001
Revises:
Create Date: 2026-08-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


rol_usuario = postgresql.ENUM(
    "admin", "empleador", "estudiante", name="rol_usuario", create_type=False
)
modalidad_oferta = postgresql.ENUM(
    "remoto", "presencial", "hibrida", name="modalidad_oferta", create_type=False
)
estado_oferta = postgresql.ENUM(
    "pendiente", "aprobada", "rechazada", name="estado_oferta", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    rol_usuario.create(bind, checkfirst=True)
    modalidad_oferta.create(bind, checkfirst=True)
    estado_oferta.create(bind, checkfirst=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("correo", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", rol_usuario, nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usuarios"),
        sa.UniqueConstraint("correo", name="uq_usuarios_correo"),
    )
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"])

    op.create_table(
        "carreras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_carreras"),
        sa.UniqueConstraint("nombre", name="uq_carreras_nombre"),
    )

    op.create_table(
        "estudiantes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("carrera_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name="fk_estudiantes_usuario", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["carrera_id"], ["carreras.id"], name="fk_estudiantes_carrera", ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_estudiantes"),
        sa.UniqueConstraint("usuario_id", name="uq_estudiantes_usuario"),
    )
    op.create_index("ix_estudiantes_carrera_id", "estudiantes", ["carrera_id"])

    op.create_table(
        "empleadores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("empresa", sa.String(length=150), nullable=False),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name="fk_empleadores_usuario", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_empleadores"),
        sa.UniqueConstraint("usuario_id", name="uq_empleadores_usuario"),
    )

    op.create_table(
        "ofertas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empleador_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("requisitos", sa.Text(), nullable=False),
        sa.Column("carrera_id", sa.Integer(), nullable=False),
        sa.Column("modalidad", modalidad_oferta, nullable=False),
        sa.Column("calle", sa.String(length=150), nullable=True),
        sa.Column("numero", sa.String(length=20), nullable=True),
        sa.Column("comuna", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column(
            "estado", estado_oferta, server_default=sa.text("'pendiente'"), nullable=False
        ),
        sa.Column("motivo_rechazo", sa.Text(), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["empleador_id"], ["empleadores.id"], name="fk_ofertas_empleador", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["carrera_id"], ["carreras.id"], name="fk_ofertas_carrera", ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ofertas"),
        # Dirección obligatoria solo si la modalidad es presencial o híbrida.
        sa.CheckConstraint(
            "(modalidad = 'remoto' AND calle IS NULL AND numero IS NULL "
            "AND comuna IS NULL AND region IS NULL) "
            "OR (modalidad IN ('presencial', 'hibrida') AND calle IS NOT NULL "
            "AND numero IS NOT NULL AND comuna IS NOT NULL AND region IS NOT NULL)",
            name="ck_ofertas_direccion_segun_modalidad",
        ),
        # El rechazo exige motivo; los demás estados no lo llevan.
        sa.CheckConstraint(
            "(estado = 'rechazada' AND motivo_rechazo IS NOT NULL) "
            "OR (estado <> 'rechazada' AND motivo_rechazo IS NULL)",
            name="ck_ofertas_motivo_rechazo",
        ),
    )
    op.create_index("ix_ofertas_empleador_id", "ofertas", ["empleador_id"])
    op.create_index("ix_ofertas_carrera_id", "ofertas", ["carrera_id"])
    op.create_index("ix_ofertas_estado", "ofertas", ["estado"])

    op.create_table(
        "postulaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("estudiante_id", sa.Integer(), nullable=False),
        sa.Column("oferta_id", sa.Integer(), nullable=False),
        sa.Column("carta_presentacion", sa.String(length=500), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["estudiante_id"],
            ["estudiantes.id"],
            name="fk_postulaciones_estudiante",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["oferta_id"], ["ofertas.id"], name="fk_postulaciones_oferta", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_postulaciones"),
        # Un estudiante no puede postular dos veces a la misma oferta.
        sa.UniqueConstraint(
            "estudiante_id", "oferta_id", name="uq_postulaciones_estudiante_oferta"
        ),
        # Carta obligatoria y de máximo 500 caracteres.
        sa.CheckConstraint(
            "char_length(carta_presentacion) BETWEEN 1 AND 500",
            name="ck_postulaciones_largo_carta",
        ),
    )
    op.create_index("ix_postulaciones_estudiante_id", "postulaciones", ["estudiante_id"])
    op.create_index("ix_postulaciones_oferta_id", "postulaciones", ["oferta_id"])


def downgrade() -> None:
    op.drop_table("postulaciones")
    op.drop_table("ofertas")
    op.drop_table("empleadores")
    op.drop_table("estudiantes")
    op.drop_table("carreras")
    op.drop_table("usuarios")

    bind = op.get_bind()
    estado_oferta.drop(bind, checkfirst=True)
    modalidad_oferta.drop(bind, checkfirst=True)
    rol_usuario.drop(bind, checkfirst=True)

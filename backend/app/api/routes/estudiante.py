from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import requiere_rol
from app.db.session import get_db
from app.models.empleador import Empleador
from app.models.enums import EstadoOferta, RolUsuario
from app.models.estudiante import Estudiante
from app.models.oferta import Oferta
from app.models.postulacion import Postulacion
from app.models.usuario import Usuario
from app.schemas.carrera import CarreraOut
from app.schemas.postulacion import OfertaEstudianteOut, PostulacionOut, PostularRequest

router = APIRouter(prefix="/estudiante", tags=["estudiante"])


def _estudiante_de(usuario: Usuario, db: Session) -> Estudiante:
    estudiante = db.scalar(
        select(Estudiante)
        .where(Estudiante.usuario_id == usuario.id)
        .options(joinedload(Estudiante.carrera))
    )
    if estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de estudiante no encontrado",
        )
    return estudiante


def _serializar_oferta(oferta: Oferta) -> OfertaEstudianteOut:
    return OfertaEstudianteOut(
        id=oferta.id,
        titulo=oferta.titulo,
        descripcion=oferta.descripcion,
        requisitos=oferta.requisitos,
        modalidad=oferta.modalidad,
        calle=oferta.calle,
        numero=oferta.numero,
        comuna=oferta.comuna,
        region=oferta.region,
        creado_en=oferta.creado_en,
        carrera=CarreraOut.model_validate(oferta.carrera),
        empresa=oferta.empleador.empresa,
    )


def _consulta_ofertas_estudiante():
    return select(Oferta).options(
        joinedload(Oferta.carrera),
        joinedload(Oferta.empleador).joinedload(Empleador.usuario),
    )


@router.get("/ofertas", response_model=list[OfertaEstudianteOut])
def listar_ofertas_disponibles(
    usuario: Usuario = Depends(requiere_rol(RolUsuario.ESTUDIANTE)),
    db: Session = Depends(get_db),
) -> list[OfertaEstudianteOut]:
    """Ofertas APROBADAS de su carrera a las que aún no ha postulado."""
    estudiante = _estudiante_de(usuario, db)
    ya_postulo = select(Postulacion.oferta_id).where(Postulacion.estudiante_id == estudiante.id)
    consulta = (
        _consulta_ofertas_estudiante()
        .where(
            Oferta.estado == EstadoOferta.APROBADA,
            Oferta.carrera_id == estudiante.carrera_id,
            Oferta.id.not_in(ya_postulo),
        )
        .order_by(Oferta.creado_en.desc())
    )
    ofertas = db.scalars(consulta).unique().all()
    return [_serializar_oferta(o) for o in ofertas]


@router.post(
    "/ofertas/{oferta_id}/postular",
    response_model=PostulacionOut,
    status_code=status.HTTP_201_CREATED,
)
def postular(
    oferta_id: int,
    datos: PostularRequest,
    usuario: Usuario = Depends(requiere_rol(RolUsuario.ESTUDIANTE)),
    db: Session = Depends(get_db),
) -> PostulacionOut:
    """Postula a una oferta aprobada de su carrera con carta de presentación."""
    estudiante = _estudiante_de(usuario, db)
    oferta = db.scalars(_consulta_ofertas_estudiante().where(Oferta.id == oferta_id)).unique().one_or_none()
    if oferta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta no encontrada")
    if oferta.estado != EstadoOferta.APROBADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede postular a ofertas aprobadas",
        )
    if oferta.carrera_id != estudiante.carrera_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta oferta no corresponde a tu carrera",
        )

    postulacion = Postulacion(
        estudiante_id=estudiante.id,
        oferta_id=oferta.id,
        carta_presentacion=datos.carta_presentacion.strip(),
    )
    db.add(postulacion)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya postulaste a esta oferta",
        ) from exc

    db.refresh(postulacion)
    return PostulacionOut(
        id=postulacion.id,
        carta_presentacion=postulacion.carta_presentacion,
        creado_en=postulacion.creado_en,
        oferta=_serializar_oferta(oferta),
    )


@router.get("/postulaciones", response_model=list[PostulacionOut])
def listar_mis_postulaciones(
    usuario: Usuario = Depends(requiere_rol(RolUsuario.ESTUDIANTE)),
    db: Session = Depends(get_db),
) -> list[PostulacionOut]:
    """Ofertas a las que el estudiante ya postuló."""
    estudiante = _estudiante_de(usuario, db)
    consulta = (
        select(Postulacion)
        .where(Postulacion.estudiante_id == estudiante.id)
        .options(
            joinedload(Postulacion.oferta).joinedload(Oferta.carrera),
            joinedload(Postulacion.oferta).joinedload(Oferta.empleador),
        )
        .order_by(Postulacion.creado_en.desc())
    )
    postulaciones = db.scalars(consulta).unique().all()
    return [
        PostulacionOut(
            id=p.id,
            carta_presentacion=p.carta_presentacion,
            creado_en=p.creado_en,
            oferta=_serializar_oferta(p.oferta),
        )
        for p in postulaciones
    ]

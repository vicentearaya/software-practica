from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import requiere_rol
from app.db.session import get_db
from app.models.carrera import Carrera
from app.models.empleador import Empleador
from app.models.enums import EstadoOferta, RolUsuario
from app.models.estudiante import Estudiante
from app.models.oferta import Oferta
from app.models.postulacion import Postulacion
from app.models.usuario import Usuario
from app.schemas.carrera import CarreraCreate, CarreraOut
from app.schemas.oferta import (
    EmpleadorResumenOut,
    EstudianteInscritoOut,
    OfertaAdminOut,
    RechazarOfertaRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _serializar_oferta(oferta: Oferta) -> OfertaAdminOut:
    empleador = oferta.empleador
    usuario = empleador.usuario
    estudiantes = [
        EstudianteInscritoOut(
            postulacion_id=p.id,
            nombre=p.estudiante.usuario.nombre,
            apellido=p.estudiante.usuario.apellido,
            correo=p.estudiante.usuario.correo,
            carrera=p.estudiante.carrera.nombre,
            carta_presentacion=p.carta_presentacion,
        )
        for p in oferta.postulaciones
    ]
    return OfertaAdminOut(
        id=oferta.id,
        titulo=oferta.titulo,
        descripcion=oferta.descripcion,
        requisitos=oferta.requisitos,
        modalidad=oferta.modalidad,
        calle=oferta.calle,
        numero=oferta.numero,
        comuna=oferta.comuna,
        region=oferta.region,
        estado=oferta.estado,
        motivo_rechazo=oferta.motivo_rechazo,
        creado_en=oferta.creado_en,
        carrera=CarreraOut.model_validate(oferta.carrera),
        empleador=EmpleadorResumenOut(
            id=empleador.id,
            empresa=empleador.empresa,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            correo=usuario.correo,
        ),
        estudiantes=estudiantes,
    )


def _consulta_ofertas_admin():
    return (
        select(Oferta)
        .options(
            joinedload(Oferta.carrera),
            joinedload(Oferta.empleador).joinedload(Empleador.usuario),
            selectinload(Oferta.postulaciones)
            .joinedload(Postulacion.estudiante)
            .options(
                joinedload(Estudiante.usuario),
                joinedload(Estudiante.carrera),
            ),
        )
        .order_by(Oferta.creado_en.desc())
    )


def _obtener_oferta(db: Session, oferta_id: int) -> Oferta | None:
    return db.scalars(_consulta_ofertas_admin().where(Oferta.id == oferta_id)).unique().one_or_none()


@router.get("/ofertas", response_model=list[OfertaAdminOut])
def listar_ofertas(
    estado: EstadoOferta | None = None,
    _: Usuario = Depends(requiere_rol(RolUsuario.ADMIN)),
    db: Session = Depends(get_db),
) -> list[OfertaAdminOut]:
    """Lista ofertas (opcionalmente filtradas por estado) con estudiantes inscritos."""
    consulta = _consulta_ofertas_admin()
    if estado is not None:
        consulta = consulta.where(Oferta.estado == estado)
    ofertas = db.scalars(consulta).unique().all()
    return [_serializar_oferta(o) for o in ofertas]


@router.post("/ofertas/{oferta_id}/aprobar", response_model=OfertaAdminOut)
def aprobar_oferta(
    oferta_id: int,
    _: Usuario = Depends(requiere_rol(RolUsuario.ADMIN)),
    db: Session = Depends(get_db),
) -> OfertaAdminOut:
    oferta = _obtener_oferta(db, oferta_id)
    if oferta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta no encontrada")
    if oferta.estado != EstadoOferta.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden aprobar ofertas pendientes",
        )
    oferta.estado = EstadoOferta.APROBADA
    oferta.motivo_rechazo = None
    db.commit()
    return _serializar_oferta(_obtener_oferta(db, oferta_id))


@router.post("/ofertas/{oferta_id}/rechazar", response_model=OfertaAdminOut)
def rechazar_oferta(
    oferta_id: int,
    datos: RechazarOfertaRequest,
    _: Usuario = Depends(requiere_rol(RolUsuario.ADMIN)),
    db: Session = Depends(get_db),
) -> OfertaAdminOut:
    oferta = _obtener_oferta(db, oferta_id)
    if oferta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta no encontrada")
    if oferta.estado != EstadoOferta.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden rechazar ofertas pendientes",
        )
    oferta.estado = EstadoOferta.RECHAZADA
    oferta.motivo_rechazo = datos.motivo.strip()
    db.commit()
    return _serializar_oferta(_obtener_oferta(db, oferta_id))


@router.post("/carreras", response_model=CarreraOut, status_code=status.HTTP_201_CREATED)
def crear_carrera(
    datos: CarreraCreate,
    _: Usuario = Depends(requiere_rol(RolUsuario.ADMIN)),
    db: Session = Depends(get_db),
) -> Carrera:
    """Agrega una carrera al catálogo (registro de estudiantes y ofertas)."""
    nombre = datos.nombre.strip()
    existe = db.scalar(select(Carrera).where(Carrera.nombre == nombre))
    if existe is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una carrera con ese nombre",
        )
    carrera = Carrera(nombre=nombre)
    db.add(carrera)
    db.commit()
    db.refresh(carrera)
    return carrera

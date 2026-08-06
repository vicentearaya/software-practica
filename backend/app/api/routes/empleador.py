from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import requiere_rol
from app.db.session import get_db
from app.models.carrera import Carrera
from app.models.empleador import Empleador
from app.models.enums import EstadoOferta, ModalidadOferta, RolUsuario
from app.models.estudiante import Estudiante
from app.models.oferta import Oferta
from app.models.postulacion import Postulacion
from app.models.usuario import Usuario
from app.schemas.carrera import CarreraOut
from app.schemas.oferta import EstudianteInscritoOut, OfertaCreate, OfertaEmpleadorOut

router = APIRouter(prefix="/empleador", tags=["empleador"])


def _empleador_de(usuario: Usuario, db: Session) -> Empleador:
    empleador = db.scalar(select(Empleador).where(Empleador.usuario_id == usuario.id))
    if empleador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de empleador no encontrado",
        )
    return empleador


def _serializar_oferta(oferta: Oferta) -> OfertaEmpleadorOut:
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
    return OfertaEmpleadorOut(
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
        cantidad_postulantes=len(estudiantes),
        estudiantes=estudiantes,
    )


def _consulta_ofertas(empleador_id: int):
    return (
        select(Oferta)
        .where(Oferta.empleador_id == empleador_id)
        .options(
            joinedload(Oferta.carrera),
            selectinload(Oferta.postulaciones)
            .joinedload(Postulacion.estudiante)
            .options(
                joinedload(Estudiante.usuario),
                joinedload(Estudiante.carrera),
            ),
        )
        .order_by(Oferta.creado_en.desc())
    )


@router.post("/ofertas", response_model=OfertaEmpleadorOut, status_code=status.HTTP_201_CREATED)
def crear_oferta(
    datos: OfertaCreate,
    usuario: Usuario = Depends(requiere_rol(RolUsuario.EMPLEADOR)),
    db: Session = Depends(get_db),
) -> OfertaEmpleadorOut:
    """Crea una oferta en estado PENDIENTE para revisión del administrador."""
    empleador = _empleador_de(usuario, db)
    carrera = db.get(Carrera, datos.carrera_id)
    if carrera is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La carrera indicada no existe",
        )

    es_remoto = datos.modalidad == ModalidadOferta.REMOTO
    oferta = Oferta(
        empleador_id=empleador.id,
        titulo=datos.titulo.strip(),
        descripcion=datos.descripcion.strip(),
        requisitos=datos.requisitos.strip(),
        carrera_id=datos.carrera_id,
        modalidad=datos.modalidad,
        calle=None if es_remoto else datos.calle,
        numero=None if es_remoto else datos.numero,
        comuna=None if es_remoto else datos.comuna,
        region=None if es_remoto else datos.region,
        estado=EstadoOferta.PENDIENTE,
    )
    db.add(oferta)
    db.commit()

    creada = db.scalars(_consulta_ofertas(empleador.id).where(Oferta.id == oferta.id)).unique().one()
    return _serializar_oferta(creada)


@router.get("/ofertas/aprobadas", response_model=list[OfertaEmpleadorOut])
def listar_ofertas_aprobadas(
    usuario: Usuario = Depends(requiere_rol(RolUsuario.EMPLEADOR)),
    db: Session = Depends(get_db),
) -> list[OfertaEmpleadorOut]:
    """Ofertas propias ya aprobadas, con cantidad e info de cada postulante."""
    empleador = _empleador_de(usuario, db)
    consulta = _consulta_ofertas(empleador.id).where(Oferta.estado == EstadoOferta.APROBADA)
    ofertas = db.scalars(consulta).unique().all()
    return [_serializar_oferta(o) for o in ofertas]

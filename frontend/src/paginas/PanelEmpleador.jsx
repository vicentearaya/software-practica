import { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth'
import CabeceraPanel from '../componentes/CabeceraPanel'

const PESTANAS = [
  { id: 'perfil', etiqueta: 'Perfil' },
  { id: 'crear', etiqueta: 'Crear oferta' },
  { id: 'aprobadas', etiqueta: 'Mis ofertas aprobadas' },
]

const FORM_INICIAL = {
  titulo: '',
  descripcion: '',
  requisitos: '',
  carrera_id: '',
  modalidad: '',
  calle: '',
  numero: '',
  comuna: '',
  region: '',
}

const ETIQUETA_MODALIDAD = {
  remoto: 'Remoto',
  presencial: 'Presencial',
  hibrida: 'Híbrida',
}

export default function PanelEmpleador() {
  const [pestana, setPestana] = useState('perfil')

  return (
    <div className="panel">
      <CabeceraPanel titulo="Panel de empleador" />

      <nav className="pestanas" aria-label="Secciones del empleador">
        {PESTANAS.map((p) => (
          <button
            key={p.id}
            type="button"
            className={pestana === p.id ? 'pestana activa' : 'pestana'}
            onClick={() => setPestana(p.id)}
          >
            {p.etiqueta}
          </button>
        ))}
      </nav>

      {pestana === 'perfil' && <PestanaPerfil />}
      {pestana === 'crear' && <PestanaCrearOferta />}
      {pestana === 'aprobadas' && <PestanaOfertasAprobadas />}
    </div>
  )
}

function PestanaPerfil() {
  const { usuario } = useAuth()

  return (
    <section className="seccion">
      <h2>Información de la cuenta</h2>
      <dl className="ficha">
        <div>
          <dt>Nombre</dt>
          <dd>{usuario.nombre}</dd>
        </div>
        <div>
          <dt>Apellido</dt>
          <dd>{usuario.apellido}</dd>
        </div>
        <div>
          <dt>Correo</dt>
          <dd>{usuario.correo}</dd>
        </div>
        <div>
          <dt>Empresa</dt>
          <dd>{usuario.empresa}</dd>
        </div>
      </dl>
    </section>
  )
}

function PestanaCrearOferta() {
  const { token } = useAuth()
  const [campos, setCampos] = useState(FORM_INICIAL)
  const [carreras, setCarreras] = useState([])
  const [error, setError] = useState(null)
  const [exito, setExito] = useState(null)
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    api.carreras().then(setCarreras).catch((e) => setError(e.message))
  }, [])

  const pideDireccion = campos.modalidad === 'presencial' || campos.modalidad === 'hibrida'

  function cambiar(evento) {
    const { name, value } = evento.target
    setCampos((previos) => ({ ...previos, [name]: value }))
  }

  async function enviar(evento) {
    evento.preventDefault()
    setError(null)
    setExito(null)
    setEnviando(true)

    const cuerpo = {
      titulo: campos.titulo,
      descripcion: campos.descripcion,
      requisitos: campos.requisitos,
      carrera_id: Number(campos.carrera_id),
      modalidad: campos.modalidad,
      ...(pideDireccion
        ? {
            calle: campos.calle,
            numero: campos.numero,
            comuna: campos.comuna,
            region: campos.region,
          }
        : {}),
    }

    try {
      const creada = await api.crearOferta(token, cuerpo)
      setExito(
        `Oferta «${creada.titulo}» enviada. Queda pendiente de aprobación del administrador.`,
      )
      setCampos(FORM_INICIAL)
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="seccion">
      <h2>Crear oferta</h2>
      <p className="tenue">
        La oferta nace en estado pendiente. El administrador debe aprobarla antes de que sea visible
        para los estudiantes.
      </p>

      <form className="form-oferta" onSubmit={enviar}>
        <label>
          Título
          <input
            name="titulo"
            value={campos.titulo}
            onChange={cambiar}
            required
            maxLength={200}
          />
        </label>

        <label>
          Descripción
          <textarea
            name="descripcion"
            value={campos.descripcion}
            onChange={cambiar}
            required
            rows={4}
          />
        </label>

        <label>
          Requisitos
          <textarea
            name="requisitos"
            value={campos.requisitos}
            onChange={cambiar}
            required
            rows={3}
          />
        </label>

        <label>
          Carrera
          <select name="carrera_id" value={campos.carrera_id} onChange={cambiar} required>
            <option value="">Selecciona una carrera…</option>
            {carreras.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
        </label>

        <label>
          Modalidad
          <select name="modalidad" value={campos.modalidad} onChange={cambiar} required>
            <option value="">Selecciona…</option>
            <option value="remoto">Remoto</option>
            <option value="presencial">Presencial</option>
            <option value="hibrida">Híbrida</option>
          </select>
        </label>

        {pideDireccion && (
          <fieldset className="direccion">
            <legend>Dirección</legend>
            <label>
              Calle
              <input name="calle" value={campos.calle} onChange={cambiar} required maxLength={150} />
            </label>
            <label>
              Número
              <input name="numero" value={campos.numero} onChange={cambiar} required maxLength={20} />
            </label>
            <label>
              Comuna
              <input name="comuna" value={campos.comuna} onChange={cambiar} required maxLength={100} />
            </label>
            <label>
              Región
              <input name="region" value={campos.region} onChange={cambiar} required maxLength={100} />
            </label>
          </fieldset>
        )}

        {error && <p className="error">{error}</p>}
        {exito && <p className="exito">{exito}</p>}

        <button type="submit" disabled={enviando}>
          {enviando ? 'Enviando…' : 'Enviar oferta'}
        </button>
      </form>
    </section>
  )
}

function PestanaOfertasAprobadas() {
  const { token } = useAuth()
  const [ofertas, setOfertas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let vigente = true
    setCargando(true)
    api
      .misOfertasAprobadas(token)
      .then((datos) => vigente && setOfertas(datos))
      .catch((e) => vigente && setError(e.message))
      .finally(() => vigente && setCargando(false))
    return () => {
      vigente = false
    }
  }, [token])

  return (
    <section className="seccion">
      <h2>Mis ofertas aprobadas</h2>

      {error && <p className="error">{error}</p>}
      {cargando && <p className="tenue">Cargando ofertas…</p>}

      {!cargando && ofertas.length === 0 && (
        <p className="vacio-inline">Aún no tienes ofertas aprobadas.</p>
      )}

      <div className="lista-ofertas">
        {ofertas.map((oferta) => (
          <article key={oferta.id} className="oferta">
            <header className="oferta-cabecera">
              <h3>{oferta.titulo}</h3>
              <span className="estado estado-aprobada">
                {oferta.cantidad_postulantes} postulante
                {oferta.cantidad_postulantes === 1 ? '' : 's'}
              </span>
            </header>

            <dl className="ficha compacta">
              <div>
                <dt>Carrera</dt>
                <dd>{oferta.carrera.nombre}</dd>
              </div>
              <div>
                <dt>Modalidad</dt>
                <dd>{ETIQUETA_MODALIDAD[oferta.modalidad]}</dd>
              </div>
              {oferta.modalidad !== 'remoto' && (
                <div>
                  <dt>Dirección</dt>
                  <dd>
                    {oferta.calle} {oferta.numero}, {oferta.comuna}, {oferta.region}
                  </dd>
                </div>
              )}
              <div>
                <dt>Descripción</dt>
                <dd>{oferta.descripcion}</dd>
              </div>
              <div>
                <dt>Requisitos</dt>
                <dd>{oferta.requisitos}</dd>
              </div>
            </dl>

            <div className="inscritos">
              <h4>Estudiantes postulados ({oferta.cantidad_postulantes})</h4>
              {oferta.estudiantes.length === 0 ? (
                <p className="tenue">Todavía no hay postulaciones.</p>
              ) : (
                <ul>
                  {oferta.estudiantes.map((est) => (
                    <li key={est.postulacion_id}>
                      <strong>
                        {est.nombre} {est.apellido}
                      </strong>{' '}
                      · {est.correo} · {est.carrera}
                      <p className="carta">{est.carta_presentacion}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

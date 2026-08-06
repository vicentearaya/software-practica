import { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth'
import CabeceraPanel from '../componentes/CabeceraPanel'

const PESTANAS = [
  { id: 'perfil', etiqueta: 'Perfil' },
  { id: 'dashboard', etiqueta: 'Dashboard' },
  { id: 'carreras', etiqueta: 'Carreras' },
]

const ESTADOS_DASHBOARD = [
  { id: 'pendiente', etiqueta: 'Pendientes de aprobación' },
  { id: 'aprobada', etiqueta: 'Aprobadas' },
  { id: 'rechazada', etiqueta: 'Rechazadas' },
]

const ETIQUETA_MODALIDAD = {
  remoto: 'Remoto',
  presencial: 'Presencial',
  hibrida: 'Híbrida',
}

export default function PanelAdministrador() {
  const [pestana, setPestana] = useState('perfil')

  return (
    <div className="panel">
      <CabeceraPanel titulo="Panel de administración" />

      <nav className="pestanas" aria-label="Secciones del administrador">
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
      {pestana === 'dashboard' && <PestanaDashboard />}
      {pestana === 'carreras' && <PestanaCarreras />}
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
      </dl>
    </section>
  )
}

function PestanaDashboard() {
  const { token } = useAuth()
  const [ofertas, setOfertas] = useState([])
  const [estadoVista, setEstadoVista] = useState('pendiente')
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [rechazandoId, setRechazandoId] = useState(null)
  const [motivo, setMotivo] = useState('')
  const [accionando, setAccionando] = useState(false)

  async function cargar() {
    setCargando(true)
    setError(null)
    try {
      setOfertas(await api.adminOfertas(token))
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [token])

  const filtradas = ofertas.filter((o) => o.estado === estadoVista)

  async function aprobar(id) {
    setAccionando(true)
    setError(null)
    try {
      const actualizada = await api.aprobarOferta(token, id)
      setOfertas((previas) => previas.map((o) => (o.id === id ? actualizada : o)))
    } catch (e) {
      setError(e.message)
    } finally {
      setAccionando(false)
    }
  }

  async function confirmarRechazo(id) {
    if (!motivo.trim()) {
      setError('El motivo de rechazo es obligatorio')
      return
    }
    setAccionando(true)
    setError(null)
    try {
      const actualizada = await api.rechazarOferta(token, id, motivo.trim())
      setOfertas((previas) => previas.map((o) => (o.id === id ? actualizada : o)))
      setRechazandoId(null)
      setMotivo('')
    } catch (e) {
      setError(e.message)
    } finally {
      setAccionando(false)
    }
  }

  return (
    <section className="seccion">
      <h2>Solicitudes de ofertas</h2>

      <div className="subpestanas">
        {ESTADOS_DASHBOARD.map((e) => {
          const cantidad = ofertas.filter((o) => o.estado === e.id).length
          return (
            <button
              key={e.id}
              type="button"
              className={estadoVista === e.id ? 'subpestana activa' : 'subpestana'}
              onClick={() => setEstadoVista(e.id)}
            >
              {e.etiqueta} ({cantidad})
            </button>
          )
        })}
      </div>

      {error && <p className="error">{error}</p>}
      {cargando && <p className="tenue">Cargando ofertas…</p>}

      {!cargando && filtradas.length === 0 && (
        <p className="vacio-inline">No hay ofertas {ESTADOS_DASHBOARD.find((e) => e.id === estadoVista)?.etiqueta.toLowerCase()}.</p>
      )}

      <div className="lista-ofertas">
        {filtradas.map((oferta) => (
          <article key={oferta.id} className="oferta">
            <header className="oferta-cabecera">
              <h3>{oferta.titulo}</h3>
              <span className={`estado estado-${oferta.estado}`}>{oferta.estado}</span>
            </header>

            <dl className="ficha compacta">
              <div>
                <dt>Empresa</dt>
                <dd>
                  {oferta.empleador.empresa} ({oferta.empleador.nombre} {oferta.empleador.apellido})
                </dd>
              </div>
              <div>
                <dt>Correo del empleador</dt>
                <dd>{oferta.empleador.correo}</dd>
              </div>
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
              {oferta.motivo_rechazo && (
                <div>
                  <dt>Motivo de rechazo</dt>
                  <dd>{oferta.motivo_rechazo}</dd>
                </div>
              )}
            </dl>

            <div className="inscritos">
              <h4>Estudiantes inscritos ({oferta.estudiantes.length})</h4>
              {oferta.estudiantes.length === 0 ? (
                <p className="tenue">Aún no hay postulaciones.</p>
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

            {oferta.estado === 'pendiente' && (
              <div className="acciones">
                {rechazandoId === oferta.id ? (
                  <div className="rechazo-form">
                    <label>
                      Motivo del rechazo
                      <textarea
                        value={motivo}
                        onChange={(e) => setMotivo(e.target.value)}
                        rows={3}
                        required
                        maxLength={2000}
                      />
                    </label>
                    <div className="acciones">
                      <button
                        type="button"
                        disabled={accionando}
                        onClick={() => confirmarRechazo(oferta.id)}
                      >
                        Confirmar rechazo
                      </button>
                      <button
                        type="button"
                        className="secundario"
                        disabled={accionando}
                        onClick={() => {
                          setRechazandoId(null)
                          setMotivo('')
                        }}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <button type="button" disabled={accionando} onClick={() => aprobar(oferta.id)}>
                      Aprobar
                    </button>
                    <button
                      type="button"
                      className="secundario peligro"
                      disabled={accionando}
                      onClick={() => {
                        setRechazandoId(oferta.id)
                        setMotivo('')
                        setError(null)
                      }}
                    >
                      Rechazar
                    </button>
                  </>
                )}
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  )
}

function PestanaCarreras() {
  const { token } = useAuth()
  const [carreras, setCarreras] = useState([])
  const [nombre, setNombre] = useState('')
  const [cargando, setCargando] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)
  const [exito, setExito] = useState(null)

  async function cargar() {
    setCargando(true)
    setError(null)
    try {
      setCarreras(await api.carreras())
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  async function enviar(evento) {
    evento.preventDefault()
    setError(null)
    setExito(null)
    setEnviando(true)
    try {
      const creada = await api.crearCarrera(token, nombre.trim())
      setCarreras((previas) =>
        [...previas, creada].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es')),
      )
      setNombre('')
      setExito(`Carrera «${creada.nombre}» agregada.`)
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="seccion">
      <h2>Carreras</h2>
      <p className="tenue">
        Estas carreras alimentan el selector del registro de estudiantes y el selector al crear una
        oferta.
      </p>

      <form className="form-inline" onSubmit={enviar}>
        <label>
          Nombre de la carrera
          <input
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
            maxLength={150}
            placeholder="Ej. Ingeniería Civil Informática"
          />
        </label>
        <button type="submit" disabled={enviando || !nombre.trim()}>
          {enviando ? 'Agregando…' : 'Agregar carrera'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
      {exito && <p className="exito">{exito}</p>}

      {cargando ? (
        <p className="tenue">Cargando carreras…</p>
      ) : (
        <ul className="lista-simple">
          {carreras.map((c) => (
            <li key={c.id}>{c.nombre}</li>
          ))}
        </ul>
      )}
    </section>
  )
}

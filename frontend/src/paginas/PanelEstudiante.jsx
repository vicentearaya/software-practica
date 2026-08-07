import { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth'
import CabeceraPanel from '../componentes/CabeceraPanel'

const PESTANAS = [
  { id: 'disponibles', etiqueta: 'Ofertas disponibles' },
  { id: 'postulaciones', etiqueta: 'Mis postulaciones' },
]

const ETIQUETA_MODALIDAD = {
  remoto: 'Remoto',
  presencial: 'Presencial',
  hibrida: 'Híbrida',
}

const MAX_CARTA = 500

export default function PanelEstudiante() {
  const [pestana, setPestana] = useState('disponibles')

  return (
    <div className="panel">
      <CabeceraPanel titulo="Panel de estudiante" />

      <nav className="pestanas" aria-label="Secciones del estudiante">
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

      {pestana === 'disponibles' && <PestanaOfertasDisponibles />}
      {pestana === 'postulaciones' && <PestanaMisPostulaciones />}
    </div>
  )
}

function DetalleOferta({ oferta }) {
  return (
    <dl className="ficha compacta">
      <div>
        <dt>Empresa</dt>
        <dd>{oferta.empresa}</dd>
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
    </dl>
  )
}

function PestanaOfertasDisponibles() {
  const { token } = useAuth()
  const [ofertas, setOfertas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [postulandoId, setPostulandoId] = useState(null)
  const [carta, setCarta] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function cargar() {
    setCargando(true)
    setError(null)
    try {
      setOfertas(await api.ofertasDisponibles(token))
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [token])

  async function confirmarPostulacion(ofertaId) {
    const texto = carta.trim()
    if (!texto) {
      setError('La carta de presentación es obligatoria')
      return
    }
    setEnviando(true)
    setError(null)
    try {
      await api.postular(token, ofertaId, texto)
      setOfertas((previas) => previas.filter((o) => o.id !== ofertaId))
      setPostulandoId(null)
      setCarta('')
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="seccion">
      <h2>Ofertas disponibles</h2>
      <p className="tenue">
        Ofertas aprobadas de tu carrera. Al postular debes incluir una carta de presentación (máx.{' '}
        {MAX_CARTA} caracteres).
      </p>

      {error && <p className="error">{error}</p>}
      {cargando && <p className="tenue">Cargando ofertas…</p>}

      {!cargando && ofertas.length === 0 && (
        <p className="vacio-inline">No hay ofertas disponibles para tu carrera por ahora.</p>
      )}

      <div className="lista-ofertas">
        {ofertas.map((oferta) => (
          <article key={oferta.id} className="oferta">
            <header className="oferta-cabecera">
              <h3>{oferta.titulo}</h3>
              <span className="estado">{oferta.empresa}</span>
            </header>

            <DetalleOferta oferta={oferta} />

            {postulandoId === oferta.id ? (
              <div className="postular-form">
                <label>
                  Carta de presentación
                  <textarea
                    value={carta}
                    onChange={(e) => setCarta(e.target.value.slice(0, MAX_CARTA))}
                    rows={4}
                    required
                    maxLength={MAX_CARTA}
                    placeholder="Explica por qué serías un buen candidato para esta oferta…"
                  />
                  <span className="tenue">
                    {carta.length}/{MAX_CARTA}
                  </span>
                </label>
                <div className="acciones">
                  <button
                    type="button"
                    disabled={enviando || !carta.trim()}
                    onClick={() => confirmarPostulacion(oferta.id)}
                  >
                    {enviando ? 'Enviando…' : 'Confirmar postulación'}
                  </button>
                  <button
                    type="button"
                    className="secundario"
                    disabled={enviando}
                    onClick={() => {
                      setPostulandoId(null)
                      setCarta('')
                      setError(null)
                    }}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            ) : (
              <div className="acciones">
                <button
                  type="button"
                  onClick={() => {
                    setPostulandoId(oferta.id)
                    setCarta('')
                    setError(null)
                  }}
                >
                  Postular
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  )
}

function PestanaMisPostulaciones() {
  const { token } = useAuth()
  const [postulaciones, setPostulaciones] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let vigente = true
    setCargando(true)
    api
      .misPostulaciones(token)
      .then((datos) => vigente && setPostulaciones(datos))
      .catch((e) => vigente && setError(e.message))
      .finally(() => vigente && setCargando(false))
    return () => {
      vigente = false
    }
  }, [token])

  return (
    <section className="seccion">
      <h2>Mis postulaciones</h2>
      <p className="tenue">Ofertas a las que ya postulaste. No vuelven a aparecer en disponibles.</p>

      {error && <p className="error">{error}</p>}
      {cargando && <p className="tenue">Cargando postulaciones…</p>}

      {!cargando && postulaciones.length === 0 && (
        <p className="vacio-inline">Aún no has postulado a ninguna oferta.</p>
      )}

      <div className="lista-ofertas">
        {postulaciones.map((p) => (
          <article key={p.id} className="oferta">
            <header className="oferta-cabecera">
              <h3>{p.oferta.titulo}</h3>
              <span className="estado estado-aprobada">Postulada</span>
            </header>

            <DetalleOferta oferta={p.oferta} />

            <div className="inscritos">
              <h4>Tu carta de presentación</h4>
              <p className="carta">{p.carta_presentacion}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { RUTA_POR_ROL, useAuth } from '../auth'

const CAMPOS_INICIALES = {
  nombre: '',
  apellido: '',
  correo: '',
  password: '',
  carrera_id: '',
  empresa: '',
}

export default function Registro() {
  const { usuario, cargando, registro } = useAuth()
  const navegar = useNavigate()

  // Lo primero que se pide es qué tipo de usuario se va a crear.
  // El administrador no aparece: se crea por seed en la base de datos.
  const [tipo, setTipo] = useState('')
  const [campos, setCampos] = useState(CAMPOS_INICIALES)
  const [carreras, setCarreras] = useState([])
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    if (tipo !== 'estudiante') return
    api.carreras().then(setCarreras).catch((e) => setError(e.message))
  }, [tipo])

  if (cargando) return <p className="centrado">Cargando…</p>
  if (usuario) return <Navigate to={RUTA_POR_ROL[usuario.rol]} replace />

  function cambiar(evento) {
    const { name, value } = evento.target
    setCampos((previos) => ({ ...previos, [name]: value }))
  }

  async function enviar(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)

    const comunes = {
      tipo,
      nombre: campos.nombre,
      apellido: campos.apellido,
      correo: campos.correo,
      password: campos.password,
    }
    const datos =
      tipo === 'estudiante'
        ? { ...comunes, carrera_id: Number(campos.carrera_id) }
        : { ...comunes, empresa: campos.empresa }

    try {
      const creado = await registro(datos)
      navegar(RUTA_POR_ROL[creado.rol], { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="pantalla-auth">
      <div className="auth-contenido">
        <div>
          <p className="marca">Prácticas</p>
          <p className="lema">Solicitud de prácticas universitarias</p>
        </div>

        <section className="tarjeta">
          <h1>Crear cuenta</h1>

            <form onSubmit={tipo ? enviar : (e) => e.preventDefault()}>
            <label>
              Tipo de usuario
              <select value={tipo} onChange={(e) => setTipo(e.target.value)} required>
                <option value="">Selecciona…</option>
                <option value="estudiante">Estudiante</option>
                <option value="empleador">Empleador</option>
              </select>
            </label>

            {tipo && (
              <>
                <div className="fila-campos">
                  <label>
                    Nombre
                    <input name="nombre" value={campos.nombre} onChange={cambiar} required />
                  </label>
                  <label>
                    Apellido
                    <input name="apellido" value={campos.apellido} onChange={cambiar} required />
                  </label>
                </div>

                <label>
                  Correo
                  <input
                    type="email"
                    name="correo"
                    value={campos.correo}
                    onChange={cambiar}
                    required
                    autoComplete="email"
                  />
                </label>
                <label>
                  Contraseña
                  <input
                    type="password"
                    name="password"
                    value={campos.password}
                    onChange={cambiar}
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                  <span className="tenue">Mínimo 8 caracteres.</span>
                </label>

                {tipo === 'estudiante' && (
                  <label>
                    Carrera
                    <select name="carrera_id" value={campos.carrera_id} onChange={cambiar} required>
                      <option value="">Selecciona tu carrera…</option>
                      {carreras.map((carrera) => (
                        <option key={carrera.id} value={carrera.id}>
                          {carrera.nombre}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                {tipo === 'empleador' && (
                  <label>
                    Empresa
                    <input name="empresa" value={campos.empresa} onChange={cambiar} required />
                  </label>
                )}

                {error && <p className="error">{error}</p>}

                <button type="submit" disabled={enviando}>
                  {enviando ? 'Creando…' : 'Crear cuenta'}
                </button>
              </>
            )}
          </form>

          <p className="tenue">
            ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
          </p>
        </section>
      </div>
    </main>
  )
}

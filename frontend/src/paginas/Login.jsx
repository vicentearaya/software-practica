import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { RUTA_POR_ROL, useAuth } from '../auth'

export default function Login() {
  const { usuario, cargando, login } = useAuth()
  const navegar = useNavigate()
  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  if (cargando) return <p className="centrado">Cargando…</p>
  if (usuario) return <Navigate to={RUTA_POR_ROL[usuario.rol]} replace />

  async function enviar(evento) {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      const datos = await login(correo, password)
      navegar(RUTA_POR_ROL[datos.rol], { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="tarjeta">
      <h1>Iniciar sesión</h1>
      <form onSubmit={enviar}>
        <label>
          Correo
          <input
            type="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={enviando}>
          {enviando ? 'Entrando…' : 'Entrar'}
        </button>
      </form>

      <p className="tenue">
        ¿No tienes cuenta? <Link to="/registro">Regístrate</Link>
      </p>
    </main>
  )
}

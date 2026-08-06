import { Navigate } from 'react-router-dom'
import { RUTA_POR_ROL, useAuth } from '../auth'

/**
 * Deja pasar solo a un usuario con sesión iniciada y con el rol indicado.
 * Es una comodidad de navegación: la autorización de verdad se verifica
 * siempre en el servidor.
 */
export default function RutaProtegida({ rol, children }) {
  const { usuario, cargando } = useAuth()

  if (cargando) return <p className="centrado">Cargando…</p>
  if (!usuario) return <Navigate to="/login" replace />
  if (rol && usuario.rol !== rol) return <Navigate to={RUTA_POR_ROL[usuario.rol]} replace />

  return children
}

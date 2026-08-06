import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from './api'

const CLAVE_TOKEN = 'practicas.token'

const ContextoAuth = createContext(null)

export function ProveedorAuth({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(CLAVE_TOKEN))
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(Boolean(localStorage.getItem(CLAVE_TOKEN)))

  // Al recargar la página revalidamos el token contra el servidor.
  useEffect(() => {
    if (!token) {
      setUsuario(null)
      setCargando(false)
      return
    }
    let vigente = true
    api
      .yo(token)
      .then((datos) => vigente && setUsuario(datos))
      .catch(() => {
        if (!vigente) return
        localStorage.removeItem(CLAVE_TOKEN)
        setToken(null)
        setUsuario(null)
      })
      .finally(() => vigente && setCargando(false))
    return () => {
      vigente = false
    }
  }, [token])

  function guardarSesion({ access_token, usuario: datosUsuario }) {
    localStorage.setItem(CLAVE_TOKEN, access_token)
    setToken(access_token)
    setUsuario(datosUsuario)
    setCargando(false)
    return datosUsuario
  }

  const valor = useMemo(
    () => ({
      token,
      usuario,
      cargando,
      login: async (correo, password) => guardarSesion(await api.login(correo, password)),
      registro: async (datos) => guardarSesion(await api.registro(datos)),
      cerrarSesion: () => {
        localStorage.removeItem(CLAVE_TOKEN)
        setToken(null)
        setUsuario(null)
      },
    }),
    [token, usuario, cargando],
  )

  return <ContextoAuth.Provider value={valor}>{children}</ContextoAuth.Provider>
}

export function useAuth() {
  const contexto = useContext(ContextoAuth)
  if (!contexto) throw new Error('useAuth debe usarse dentro de <ProveedorAuth>')
  return contexto
}

// Cada rol entra a su propio panel.
export const RUTA_POR_ROL = {
  admin: '/admin',
  empleador: '/empleador',
  estudiante: '/estudiante',
}

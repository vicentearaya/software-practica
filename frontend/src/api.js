const BASE = '/api'

async function pedir(ruta, { metodo = 'GET', cuerpo, token } = {}) {
  const respuesta = await fetch(`${BASE}${ruta}`, {
    method: metodo,
    headers: {
      ...(cuerpo ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  })

  const texto = await respuesta.text()
  const datos = texto ? JSON.parse(texto) : null

  if (!respuesta.ok) {
    throw new Error(mensajeDeError(datos) || `Error ${respuesta.status}`)
  }
  return datos
}

// FastAPI devuelve `detail` como texto (HTTPException) o como lista (validación).
function mensajeDeError(datos) {
  const detalle = datos?.detail
  if (!detalle) return null
  if (typeof detalle === 'string') return detalle
  if (Array.isArray(detalle)) return detalle.map((e) => e.msg).join(' · ')
  return null
}

export const api = {
  registro: (datos) => pedir('/auth/registro', { metodo: 'POST', cuerpo: datos }),
  login: (correo, password) =>
    pedir('/auth/login', { metodo: 'POST', cuerpo: { correo, password } }),
  yo: (token) => pedir('/auth/yo', { token }),
  carreras: () => pedir('/carreras'),
  adminOfertas: (token, estado) =>
    pedir(`/admin/ofertas${estado ? `?estado=${estado}` : ''}`, { token }),
  aprobarOferta: (token, ofertaId) =>
    pedir(`/admin/ofertas/${ofertaId}/aprobar`, { metodo: 'POST', token }),
  rechazarOferta: (token, ofertaId, motivo) =>
    pedir(`/admin/ofertas/${ofertaId}/rechazar`, {
      metodo: 'POST',
      token,
      cuerpo: { motivo },
    }),
  crearCarrera: (token, nombre) =>
    pedir('/admin/carreras', { metodo: 'POST', token, cuerpo: { nombre } }),
}

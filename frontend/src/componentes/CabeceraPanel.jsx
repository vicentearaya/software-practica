import { useAuth } from '../auth'

export default function CabeceraPanel({ titulo }) {
  const { usuario, cerrarSesion } = useAuth()

  return (
    <header className="cabecera">
      <div className="cabecera-identidad">
        <p className="marca-mini">Prácticas</p>
        <h1>{titulo}</h1>
        <p className="tenue">
          {usuario.nombre} {usuario.apellido} · {usuario.correo}
        </p>
      </div>
      <button type="button" className="secundario" onClick={cerrarSesion}>
        Cerrar sesión
      </button>
    </header>
  )
}

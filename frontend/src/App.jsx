import { Navigate, Route, Routes } from 'react-router-dom'
import RutaProtegida from './componentes/RutaProtegida'
import { RUTA_POR_ROL, useAuth } from './auth'
import Login from './paginas/Login'
import PanelAdministrador from './paginas/PanelAdministrador'
import PanelEmpleador from './paginas/PanelEmpleador'
import PanelEstudiante from './paginas/PanelEstudiante'
import Registro from './paginas/Registro'

function Inicio() {
  const { usuario, cargando } = useAuth()
  if (cargando) return <p className="centrado">Cargando…</p>
  // Lo primero que ve quien entra sin sesión es el login.
  return <Navigate to={usuario ? RUTA_POR_ROL[usuario.rol] : '/login'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />

      <Route
        path="/admin"
        element={
          <RutaProtegida rol="admin">
            <PanelAdministrador />
          </RutaProtegida>
        }
      />
      <Route
        path="/empleador"
        element={
          <RutaProtegida rol="empleador">
            <PanelEmpleador />
          </RutaProtegida>
        }
      />
      <Route
        path="/estudiante"
        element={
          <RutaProtegida rol="estudiante">
            <PanelEstudiante />
          </RutaProtegida>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

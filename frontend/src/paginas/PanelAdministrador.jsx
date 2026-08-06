import CabeceraPanel from '../componentes/CabeceraPanel'

/**
 * Panel vacío del administrador.
 * Sus pestañas (Perfil, Dashboard, Carreras) se implementan en la rama del rol.
 */
export default function PanelAdministrador() {
  return (
    <div className="panel">
      <CabeceraPanel titulo="Panel de administración" />
      <section className="vacio">
        <p>Panel vacío. Las pestañas del administrador se implementan en su propia rama.</p>
      </section>
    </div>
  )
}

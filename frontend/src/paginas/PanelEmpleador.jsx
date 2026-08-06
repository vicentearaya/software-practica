import CabeceraPanel from '../componentes/CabeceraPanel'

/**
 * Panel vacío del empleador.
 * Sus pestañas (Perfil, Crear oferta, Mis ofertas aprobadas) se implementan
 * en la rama del rol.
 */
export default function PanelEmpleador() {
  return (
    <div className="panel">
      <CabeceraPanel titulo="Panel de empleador" />
      <section className="vacio">
        <p>Panel vacío. Las pestañas del empleador se implementan en su propia rama.</p>
      </section>
    </div>
  )
}

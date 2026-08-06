import CabeceraPanel from '../componentes/CabeceraPanel'

/**
 * Panel vacío del estudiante.
 * Sus pestañas (Ofertas disponibles, Mis postulaciones) se implementan en la
 * rama del rol.
 */
export default function PanelEstudiante() {
  return (
    <div className="panel">
      <CabeceraPanel titulo="Panel de estudiante" />
      <section className="vacio">
        <p>Panel vacío. Las pestañas del estudiante se implementan en su propia rama.</p>
      </section>
    </div>
  )
}

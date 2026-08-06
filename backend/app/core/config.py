from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    """Configuración de la aplicación, leída desde variables de entorno."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://practicas:practicas@db:5432/practicas"

    jwt_secret: str = "dev-secret-cambiar-en-produccion"
    jwt_algoritmo: str = "HS256"
    jwt_expiracion_minutos: int = 60 * 8

    cors_origenes: str = "http://localhost:5173"

    # Datos de arranque (seed)
    seed_admin_nombre: str = "Admin"
    seed_admin_apellido: str = "Universidad"
    seed_admin_correo: str = "admin@universidad.cl"
    seed_admin_password: str = "admin123"
    seed_carreras: str = (
        "Ingeniería Civil Informática,"
        "Ingeniería en Ejecución Informática,"
        "Ingeniería Comercial,"
        "Contador Auditor,"
        "Diseño Gráfico"
    )

    @property
    def lista_cors_origenes(self) -> list[str]:
        return [o.strip() for o in self.cors_origenes.split(",") if o.strip()]

    @property
    def lista_seed_carreras(self) -> list[str]:
        return [c.strip() for c in self.seed_carreras.split(",") if c.strip()]


configuracion = Configuracion()

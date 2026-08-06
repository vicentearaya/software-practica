# Plataforma de solicitud de prácticas

Base del proyecto. La fuente de verdad del producto es [`ESPECIFICACION.md`](ESPECIFICACION.md).

Stack: **FastAPI + SQLAlchemy + Alembic**, **PostgreSQL**, **React (Vite)**, todo con **Docker Compose**.

## Levantar todo

```bash
docker compose up --build
```

| Servicio | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| API | http://localhost:8000/api |
| Documentación de la API | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

Al arrancar, el backend espera a la base de datos, aplica las migraciones
(`alembic upgrade head`) y ejecuta el seed (idempotente).

Credenciales del administrador creadas por el seed:

```
correo:     admin@universidad.cl
contraseña: admin123
```

Para cambiar cualquier valor por defecto, copia `.env.example` como `.env`.

## Qué está implementado

- Migración inicial (`0001`) con **todas** las tablas de la especificación:
  `usuarios`, `carreras`, `estudiantes`, `empleadores`, `ofertas`, `postulaciones`,
  con sus restricciones (correo único, unicidad estudiante+oferta, dirección
  obligatoria si la modalidad no es remota, motivo obligatorio al rechazar,
  carta de máximo 500 caracteres).
- Registro y login con contraseña hasheada (bcrypt) y JWT.
- El registro pide primero el tipo de usuario; **administrador no es registrable**.
- Cada rol entra a su panel, todavía vacío.
- Seed: un administrador y las carreras iniciales.

Endpoints disponibles:

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/api/auth/registro` | Crea estudiante o empleador y devuelve token |
| POST | `/api/auth/login` | Devuelve token |
| GET | `/api/auth/yo` | Usuario de la sesión activa |
| GET | `/api/carreras` | Catálogo para el selector del registro |
| GET | `/api/salud` | Healthcheck |

## Qué falta (una rama por rol)

Las pestañas y endpoints de administrador, empleador y estudiante. **Ninguna
rama debe crear migraciones nuevas**: el esquema completo ya está en `0001`.

Puntos de extensión pensados para minimizar conflictos entre ramas:

- Backend: un router nuevo en `backend/app/api/routes/` montado en `app/main.py`,
  protegido con `requiere_rol(...)` de `app/api/deps.py`.
- Frontend: cada panel tiene su propio archivo en `frontend/src/paginas/`.

## Comandos útiles

```bash
docker compose logs -f backend        # ver logs de la API
docker compose exec backend alembic current
docker compose exec db psql -U practicas -d practicas
docker compose down                   # detener
docker compose down -v                # detener y borrar la base de datos
```

#!/bin/sh
set -e

echo "→ Esperando a PostgreSQL..."
python - <<'PY'
import time

import sqlalchemy

from app.core.config import configuracion

motor = sqlalchemy.create_engine(configuracion.database_url)
for intento in range(1, 31):
    try:
        with motor.connect() as conexion:
            conexion.execute(sqlalchemy.text("SELECT 1"))
        print("   base de datos disponible")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"   intento {intento}/30: {exc.__class__.__name__}")
        time.sleep(2)
else:
    raise SystemExit("No se pudo conectar a la base de datos")
PY

echo "→ Aplicando migraciones (alembic upgrade head)..."
alembic upgrade head

echo "→ Cargando datos de arranque (seed)..."
python -m app.seed

echo "→ Levantando la API en http://localhost:8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

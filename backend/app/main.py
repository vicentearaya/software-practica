from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, carreras
from app.core.config import configuracion

app = FastAPI(
    title="Plataforma de solicitud de prácticas",
    description="Base del proyecto: acceso (registro y login) y modelo de datos completo.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.lista_cors_origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(carreras.router, prefix="/api")

# Aquí se montan después los routers de cada rol (cada uno en su propia rama):
#   app.include_router(admin.router, prefix="/api")
#   app.include_router(empleador.router, prefix="/api")
#   app.include_router(estudiante.router, prefix="/api")


@app.get("/api/salud", tags=["salud"])
def salud() -> dict[str, str]:
    return {"estado": "ok"}

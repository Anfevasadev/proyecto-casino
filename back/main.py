# -------------------------------------------
# back/main.py
# Propósito:
#   - Punto de entrada de la aplicación FastAPI.
#   - Crear la instancia "app", definir el endpoint básico /health,
#     y montar el router principal de la API (back/api/router.py) bajo /api.
#
# Librerías a usar:
#   - from fastapi import FastAPI
#   - (Opcional) from fastapi.middleware.cors import CORSMiddleware, si el front requiere CORS
#   - from api.router import api_router
#
# Estructura esperada:
#   1) app = FastAPI(title="Cuadre Casino", version="0.1.0")
#   2) Definir un endpoint de salud "rápido" en "/" o "/health":
#        @app.get("/health")
#        def health(): return {"status": "ok"}
#      * Este health NO debe depender de CSV ni de nada externo para no fallar.
#   3) Incluir el router de la API versionada:
#        app.include_router(api_router, prefix="/api")
#      * Esto montará /api/v1/health, /api/v1/users, /api/v1/places, /api/v1/machines, etc.
#   4) (Opcional) Configurar CORS si el front está en otro origen (localhost:puerto):
#        app.add_middleware(CORSMiddleware, allow_origins=["*"] o la lista concreta,
#                           allow_methods=["*"], allow_headers=["*"])
#
# Convenciones:
#   - No colocar lógica de negocio aquí.
#   - Mantener el archivo simple para que el equipo arranque Uvicorn sin confusión:
#       uvicorn back.main:app --reload
#
# Notas:
#   - La API trabaja con datos en CSV dentro de /data (hora local).
#   - Si en el futuro se agregan "eventos" de inicio (startup) para preparar rutas
#     u otro setup, documentarlo aquí con claridad (pero mantenerlo mínimo por ser académico).
# ----------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router


def create_app() -> FastAPI:
    """Factory to create and configure the FastAPI application.

    Returns
    -------
    FastAPI
        Configured application ready to run with Uvicorn.
    """
    app = FastAPI(title="Demo Cuadre Casino", version="0.1.0")

    # Configuración CORS para permitir peticiones desde el front (Vite por defecto en 5173)
    allowed_origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        """Simple health check endpoint.

        Returns a JSON payload indicating the service is running.

        Returns
        -------
        dict[str, str]
            A status payload containing a static message.
        """
        return {"status": "ok"}

    # Mount the versioned API under /api. Additional routers may be added
    # inside api/router.py.
    app.include_router(api_router, prefix="/api")
    return app


# Application instance used by Uvicorn. When running ``uvicorn back.main:app``
# Uvicorn will import this module and look for an ``app`` attribute. The
# ``create_app`` factory is called to ensure fresh configuration on import.
app = create_app()
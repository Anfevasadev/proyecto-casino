# -------------------------------------------
# back/api/router.py
# Propósito:
#   - Declarar un APIRouter "raíz" e incluir los routers de cada recurso/versión.
#   - Definir prefijos, tags y versionamiento (p. ej., /api/v1).
#
# Qué debe exponer:
#   - Una variable "api_router" de tipo APIRouter que sea incluida por back/main.py.
#
# Contenido esperado:
#   - Importa APIRouter desde fastapi.
#   - Importa routers de back/api/v1 (health, users, places, machines).
#   - Crea "api_router = APIRouter()" e incluye:
#       api_router.include_router(health.router,  prefix="/v1",         tags=["health"])
#       api_router.include_router(users.router,   prefix="/v1/users",   tags=["users"])
#       api_router.include_router(places.router,  prefix="/v1/places",  tags=["places"])
#       api_router.include_router(machines.router,prefix="/v1/machines",tags=["machines"])
#       Y así sucesivamente para otros recursos.
#
# Reglas/decisiones:
#   - Mantener versionamiento en el path (ej.: /api/v1/*) para que futuras
#     versiones convivan sin romper clientes.
#   - No colocar lógica de negocio aquí, solo "enrutamiento".
# -------------------------------------------

from fastapi import APIRouter

# Router del modulo de login
from back.api.v1.auth import router as auth_router 
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router, tags=["auth"]) 


# Router del modulo de machines
from back.api.v1.machines import router as machines_router
api_router.include_router(machines_router, tags=["machines"])
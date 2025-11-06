# -------------------------------------------
# back/api/v1/health.py
# Propósito:
#   Exponer un endpoint de "health" para monitorear si la API está viva.
#
# Router esperado:
#   - Variable "router" = APIRouter()
#
# Endpoints:
#   GET /health
#     - Entradas: ninguna.
#     - Procesamiento: no hace IO; simplemente responde un dict estático.
#     - Salida (200): {"status":"ok","version":"v1"}
#     - Errores: ninguno esperado.
#
# Librerías:
#   - from fastapi import APIRouter
#
# Notas:
#   - Mantenerlo minimalista para que siempre funcione, incluso si el resto falla.
# -------------------------------------------

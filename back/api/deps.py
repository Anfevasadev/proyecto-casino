# -------------------------------------------
# back/api/deps.py
# Propósito:
#   Centralizar "dependencias" de FastAPI (funciones que se inyectan en endpoints).
#   Ejemplos: acceso a repositorios CSV, validación simple de headers, paginación, etc.
#
# Dependencias típicas (ideas):
#   1) get_repos()
#      - Entradas: ninguna (o config mínima).
#      - Procesamiento: inicializa y retorna objetos "repositorio" que saben
#        leer/escribir CSV (users_repo, places_repo, etc.).
#      - Salida: un dict o un objeto con referencias a repos, p.ej.:
#          { "users": users_repo, "places": places_repo, ... }
#      - Uso: como "Depends(get_repos)" dentro de endpoints para no repetir import/instancia.
#
#   2) pagination_params()
#      - Entradas: query params opcionales "limit" (int), "offset" (int).
#      - Validaciones: ambos >= 0; "limit" con tope razonable (p. ej., 100).
#      - Salida: tupla o dict con limit y offset saneados.
#
#   3) filter_active_param()
#      - Entradas: query param "only_active" (bool=true por defecto).
#      - Salida: bool para filtrar en repos/servicio si se devuelven solo activos.
#
# Librerías a usar:
#   - from fastapi import Depends, Query, Header (según necesitemos).
#
# Notas:
#   - Mantener las dependencias simples (proyecto académico).
#   - No implementar autenticación aquí por ahora (usuarios/contraseñas están en CSV,
#     pero la seguridad se agregaría más adelante si se requiere).
# -------------------------------------------

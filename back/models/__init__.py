# -------------------------------------------
# back/models/__init__.py
# Propósito:
#   - Marcar el directorio como paquete.
#   - Documentar lineamientos generales de modelos Pydantic usados por la API.
#
# Lineamientos:
#   - Usar Pydantic (v2) para definir modelos de request/response.
#   - Mantener separación clara entre modelos de ENTRADA (p. ej., UserIn)
#     y modelos de SALIDA (p. ej., UserOut). Los de salida no deben exponer
#     campos sensibles (como password).
#   - Tipos base:
#       * int para IDs.
#       * str para texto.
#       * float/Decimal para montos (si se prefiere precisión, usar Decimal y documentar).
#       * bool para flags como is_active.
#       * str para fechas/horas en formato local 'YYYY-MM-DD HH:MM:SS' (si no se
#         quiere usar datetime nativo). Consistencia > sofisticación.
#   - Validaciones:
#       * Usar validadores para rangos (ej.: participation_rate ∈ [0,1]).
#       * Usar enumeraciones para valores acotados (roles).
#       * Normalizar strings (strip) donde aplique (username, name, code).
#   - Compatibilidad CSV:
#       * Estos modelos reflejan las columnas que realmente se guardan/leen
#         en CSV. Si un campo no se almacena, no debe estar en el modelo de salida.
#   - Convención de nombres:
#       * <Entidad>In  = request para crear/actualizar (entrada).
#       * <Entidad>Out = respuesta hacia cliente (salida).
#       * <Entidad>Update = request de actualización parcial si aplica.
# -------------------------------------------

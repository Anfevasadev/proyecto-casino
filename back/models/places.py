# -------------------------------------------
# back/models/places.py
# Propósito:
#   - Contratos Pydantic para "lugares" (casinos/salas).
#
# Modelos esperados:
#   1) PlaceIn (crear):
#       - name: str (obligatorio; único; aplicar .strip()).
#       - address: str | None (opcional; .strip()).
#       - is_active: bool (default True).
#     Validaciones:
#       * name no vacío; longitud razonable (ej.: 1..100) opcional.
#
#   2) PlaceUpdate (actualizar):
#       - name: str | None (misma validación si viene).
#       - address: str | None.
#       - is_active: bool | None.
#
#   3) PlaceOut (salida):
#       - id: int
#       - name: str
#       - address: str | None
#       - is_active: bool
#
# Notas:
#   - Campos de auditoría no se exponen por defecto.
#   - Borrado lógico = is_active False; no existen campos is_deleted aquí.
# -------------------------------------------

# -------------------------------------------
# back/domain/places/__init__.py
# Propósito:
#   Documentar la lógica de "lugares" (casinos/salas).
#
# Entidad places (CSV: data/places.csv):
#   - Campos: id, name (único), address (opcional), is_active, auditoría created_/updated_.
#
# Políticas:
#   - Borrado lógico = is_active=False.
#   - Si un place se desactiva, el dominio puede impedir crear nuevas máquinas
#     asociadas a ese place (validación cruzada en domain/machines o en repos).
#
# Operaciones previstas:
#   - create_place(data)
#   - listar_places(filtros)
#   - obtener_place(id)
#   - actualizar_place(id, cambios)
#   - desactivar_place(id)
# -------------------------------------------
from .management import CasinoManagement

__all__ = ["CasinoManagement"]

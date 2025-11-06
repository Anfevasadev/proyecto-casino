# -------------------------------------------
# back/domain/__init__.py
# Propósito:
#   Marca el paquete "domain" y sirve como punto de documentación general.
#
# Qué vive en "domain":
#   - Reglas/operaciones por entidad (users, places, counters).
#   - Cada operación (create/read/update/delete) idealmente es una función
#     que NO conoce FastAPI ni detalles HTTP. Solo recibe datos Python y
#     usa repositorios para persistir/leer.
#
# Reglas generales:
#   - Tiempos en hora local (formato 'YYYY-MM-DD HH:MM:SS').
#   - Borrado lógico = cambiar "is_active" a False (no eliminar filas).
#   - IDs se obtienen del repositorio (next_id) y son únicos.
#   - Validar datos antes de persistir; retornar errores mediante excepciones
#     específicas (o dicts de error si prefieren). La traducción a HTTP la hace la capa API.
#
# No colocar importaciones pesadas aquí; evitar dependencias cíclicas.
# -------------------------------------------

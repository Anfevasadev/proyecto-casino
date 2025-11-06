# -------------------------------------------
# back/tests/__init__.py
# Propósito:
#   - Marcar el directorio de pruebas.
#   - Documentar convenciones de testing para el equipo.
#
# Convenciones de pruebas:
#   - Usar pytest como runner.
#   - Tests "mínimos felices" primero (no cubrir todas las ramas al inicio).
#   - Evitar dependencias externas; levantar la app FastAPI en memoria con TestClient.
#   - No modificar CSV reales en pruebas básicas:
#       * Sugerencia: antes de cada test, crear copias temporales en un directorio
#         temporal y apuntar los repos a esas rutas (o mockear rutas).
#       * Alternativa minimalista: usar archivos CSV "sandbox" y limpiarlos al final.
#   - Nomenclatura de archivos: test_*.py; funciones: test_*.
# -------------------------------------------

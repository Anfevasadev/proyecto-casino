# -------------------------------------------
# back/core/__init__.py
# Propósito:
#   - Marcar el paquete "core".
#   - Centralizar documentación de configuración general del proyecto.
#
# Qué vive en "core":
#   - Parámetros compartidos: rutas base, formato de hora local, constantes de paginación,
#     y utilidades simples relacionadas con configuración (no lógica de negocio).
#
# Reglas:
#   - Mantener este paquete minimalista; NO incluir dependencias de dominio/API/storage
#     para evitar ciclos.
#   - Si se requiere leer variables de entorno en el futuro, documentar aquí la convención
#     (pero para el proyecto académico, mantener todo "hardcoded" en settings.py).
# -------------------------------------------

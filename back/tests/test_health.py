# -------------------------------------------
# back/tests/test_health.py
# Propósito:
#   - Verificar que el endpoint de salud funcione y que la app arranque.
#
# Qué debe probar:
#   1) GET /health  (ruta sin prefijo /api para el health básico)
#      - Entrada: ninguna.
#      - Proceso: realizar una petición GET con TestClient a "/health".
#      - Salida esperada:
#          * status_code == 200
#          * cuerpo JSON con al menos {"status": "ok"}
#
#   2) GET /api/v1/health (si está montado)
#      - Entrada: ninguna.
#      - Salida esperada:
#          * status_code == 200
#          * JSON con {"status": "ok", "version": "v1"} o similar.
#
# Consideraciones:
#   - Este test NO toca CSV; debe pasar aún si /data/ está vacío.
#   - Evitar sleeps o dependencias externas.
# -------------------------------------------

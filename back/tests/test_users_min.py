# -------------------------------------------
# back/tests/test_users_min.py
# Propósito:
#   - Validar el flujo mínimo de usuarios: crear y listar.
#
# Preparación:
#   - Asegurar que los repos apunten a CSVs de prueba (no a los de producción en /data).
#     Opciones:
#       * Usar tmpdir/TemporaryDirectory y copiar encabezados vacíos.
#       * Mockear las rutas de back/storage/csv_paths.py para apuntar al tmp.
#
# Casos a cubrir (mínimos):
#   1) Crear usuario feliz (POST /api/v1/users/)
#      - Entrada (JSON): {"username":"ana","password":"123","role":"operador"}
#      - Validaciones esperadas por la API/dominio:
#          * username no vacío
#          * role permitido
#      - Salida:
#          * status_code == 201
#          * JSON con campos públicos: id, username, role, is_active (True por defecto).
#          * No debe exponer "password".
#
#   2) Listar usuarios (GET /api/v1/users/)
#      - Entrada: none o query simples (limit/offset).
#      - Salida:
#          * status_code == 200
#          * JSON = lista con al menos el usuario creado en (1).
#
#   3) Username duplicado (POST /api/v1/users/)
#      - Entrada: repetir "ana".
#      - Salida:
#          * status_code == 400 (o el código acordado)
#          * JSON con mensaje de error indicando duplicidad.
#
# Reglas/Notas:
#   - No verificar auditoría aquí (created_at/by...); mantener test minimalista.
#   - Asegurarse de limpiar o aislar CSVs de prueba entre tests para evitar contaminación.
# -------------------------------------------

# -------------------------------------------
# back/tests/test_machines_min.py
# Propósito:
#   - Validar flujo mínimo de máquinas: crear lugar, crear máquina, listar.
#
# Preparación:
#   - Igual que en usuarios: usar CSVs de prueba o mock de rutas a un tmpdir.
#   - Crear primero un "place" activo para usar su id en la máquina (FK lógica).
#
# Casos a cubrir (mínimos):
#   1) Crear lugar feliz (POST /api/v1/places/)
#      - Entrada: {"name":"Casino Centro","address":"Calle 1","is_active":true}
#      - Salida:
#          * 201
#          * JSON con {id, name, address, is_active}
#
#   2) Crear máquina feliz (POST /api/v1/machines/)
#      - Entrada: {
#           "code": "M-001",
#           "denomination_value": 100.0,
#           "place_id": <id_place_creado>,
#           "participation_rate": 0.5,
#           "is_active": true
#        }
#      - Validaciones esperadas:
#           * code único (no duplicado).
#           * place_id existente y activo.
#           * denomination_value >= 0.
#           * participation_rate en [0,1].
#      - Salida:
#           * 201
#           * JSON con los campos públicos de MachineOut.
#
#   3) Listar máquinas (GET /api/v1/machines/)
#      - Entrada: opcionalmente place_id=<id_place_creado>.
#      - Salida:
#           * 200
#           * Lista con al menos la máquina creada.
#
#   4) Error por place inexistente (POST /api/v1/machines/)
#      - Entrada: igual a (2) pero con place_id que no existe.
#      - Salida:
#           * 404 (o 400 según convención)
#           * Mensaje que indique que el lugar no existe o está inactivo.
#
# Reglas/Notas:
#   - Mantener los tests directos, sin mocks sofisticados.
#   - No probar aún counters ni balances aquí; se hará en otros archivos.
# -------------------------------------------

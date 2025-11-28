# -------------------------------------------
# back/domain/machines/create.py
# Función esperada: create_machine(data, clock, machines_repo, places_repo, actor)
#
# Entradas:
#   - data: dict o modelo con:
#       code (string, obligatorio, único),
#       denomination_value (decimal >= 0, obligatorio),
#       place_id (int, obligatorio y existente),
#       participation_rate (decimal en [0,1], por defecto 1.0 si no se informa),
#       is_active (bool, por defecto True).
#   - clock: función que devuelve hora local 'YYYY-MM-DD HH:MM:SS' (inyectable para test).
#   - machines_repo: repositorio CSV de máquinas (next_id, existe_code, insertar, etc.).
#   - places_repo: repositorio CSV de places (para validar existencia/estado activo).
#   - actor: string con el usuario (o 'system') para auditoría.
#
# Validaciones:
#   - code obligatorio, trim y único (no permitir repetidos).
#   - denomination_value debe ser numérico y >= 0.
#   - participation_rate numérico dentro de [0,1].
#   - place_id debe existir en places y estar is_active=True.
#
# Procesamiento:
#   1) Verificar validaciones anteriores.
#   2) Asignar id = machines_repo.next_id().
#   3) Construir fila con auditoría:
#        created_at/by = clock()/actor; updated_at/by = clock()/actor.
#   4) Insertar fila en CSV a través del repo.
#
# Salida (retorno):
#   - Dict/obj público con {id, code, denomination_value, place_id, participation_rate, is_active}.
#
# Errores:
#   - ValueError/DomainError por duplicado/valores fuera de rango.
#   - NotFoundError si place_id no existe (o está inactivo).
# -------------------------------------------
from back.models.machines import MachineIn, MachineOut
from back.storage.machines_repo import MachinesRepo
from datetime import datetime

def registrarMaquina(data: MachineIn, clock, machines_repo: MachinesRepo, actor: str):
    # Validaciones básicas
    if not data.marca or not data.modelo or not data.serial or not data.asset or not data.denominacion:
        raise ValueError("Todos los campos obligatorios deben ser completados")

    # Validar unicidad serial/asset
    if machines_repo.existe_serial_o_asset(data.serial, data.asset):
        raise ValueError("Serial o Asset ya registrado")

    # Crear ID
    nuevo_id = machines_repo.next_id()

    # Construir MachineOut
    nueva_maquina = MachineOut(
        id=nuevo_id,
        marca=data.marca,
        modelo=data.modelo,
        serial=data.serial,
        asset=data.asset,
        denominacion=data.denominacion,
        estado=data.is_active,
        casino_id=data.place_id  # temporal, mientras no se valida casino
    )

    # Guardar en CSV
    machines_repo.agregar(nueva_maquina, actor, clock.now())
    return nueva_maquina

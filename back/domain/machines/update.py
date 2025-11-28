# -------------------------------------------
# back/domain/machines/update.py
# Propósito:
#   Función para actualizar máquinas registradas.
#   Restricción: La denominación NO puede modificarse.
#
# Validaciones:
#   - machine_id debe existir.
#   - No se permite modificar: id, denominacion, created_at, created_by.
#   - Si se cambia serial: debe ser único (excluyendo la máquina actual).
#   - Si se cambia asset: debe ser único (excluyendo la máquina actual).
#   - Si se cambia casino_id: el casino debe existir e estar activo.
#
# Salida:
#   - Dict actualizado o excepción si hay error.
# -------------------------------------------

class ActualizacionMaquinaError(Exception):
    """Excepción para errores en actualización de máquinas."""
    pass


def actualizar_maquina(
    machine_id: int,
    cambios: dict,
    machines_repo,
    places_repo,
    actor: str = "system"
):
    """
    Actualiza una máquina con las restricciones especificadas.
    
    Args:
        machine_id: ID de la máquina a actualizar.
        cambios: Dict con campos a actualizar (marca, modelo, serial, asset, casino_id).
        machines_repo: Repositorio de máquinas.
        places_repo: Repositorio de casinos.
        actor: Usuario que realiza la actualización.
    
    Returns:
        Dict con la máquina actualizada.
    
    Raises:
        ActualizacionMaquinaError: Si hay error en la validación o actualización.
    """
    
    # 1. Verificar que la máquina existe
    maquina_actual = machines_repo.get_by_id(machine_id)
    if maquina_actual is None:
        raise ActualizacionMaquinaError(f"Máquina con ID {machine_id} no encontrada")
    
    # 2. Validar que no se intente modificar campos prohibidos
    campos_prohibidos = ["id", "denominacion", "created_at", "created_by"]
    for campo in campos_prohibidos:
        if campo in cambios and cambios[campo] is not None:
            raise ActualizacionMaquinaError(f"No se puede modificar el campo '{campo}'")
    
    # 3. Validar unicidad de serial (si se proporciona cambio)
    if "serial" in cambios and cambios["serial"] is not None:
        if machines_repo.existe_serial(cambios["serial"], exclude_id=machine_id):
            raise ActualizacionMaquinaError(
                f"Ya existe otra máquina con el serial '{cambios['serial']}'"
            )
    
    # 4. Validar unicidad de asset (si se proporciona cambio)
    if "asset" in cambios and cambios["asset"] is not None:
        if machines_repo.existe_asset(cambios["asset"], exclude_id=machine_id):
            raise ActualizacionMaquinaError(
                f"Ya existe otra máquina con el asset '{cambios['asset']}'"
            )
    
    # 5. Validar que el casino existe e está activo (si se proporciona cambio)
    if "casino_id" in cambios and cambios["casino_id"] is not None:
        # Convertir a int si es necesario
        casino_id = int(cambios["casino_id"]) if isinstance(cambios["casino_id"], str) else cambios["casino_id"]
        casino = places_repo.obtener_por_id(casino_id)
        if casino is None:
            raise ActualizacionMaquinaError(
                f"Casino con ID {casino_id} no encontrado"
            )
        # Validar que el casino esté activo
        estado = casino.get("estado")
        if estado is not None and str(estado).lower() == "false":
            raise ActualizacionMaquinaError(
                f"Casino con ID {casino_id} está inactivo"
            )
    
    # 6. Realizar la actualización
    maquina_actualizada = machines_repo.actualizar(machine_id, cambios, actor)
    
    if maquina_actualizada is None:
        raise ActualizacionMaquinaError(
            f"No se pudo actualizar la máquina con ID {machine_id}"
        )
    
    return maquina_actualizada

from pathlib import Path
from datetime import datetime
from typing import Optional, List

import pandas as pd

from back.storage.places_repo import PlaceStorage
from back.storage.machines_repo import MachinesRepo
from back.models.places import PlaceOut, PlaceIn


DATA_DIR = Path(__file__).parent.parent.parent / "data"
PLACES_CSV = DATA_DIR / "places.csv"


class CasinoManagement:
    """Operaciones de gestión de casinos (alta, modificación, inactivación, consultas).

    Reglas destacadas:
    - `codigo_casino` es inmutable: no se permite su modificación.
    - Se valida unicidad de `nombre` al modificar.
    - Se delega creación e inactivación a `PlaceStorage`/`PlaceDomain` cuando aplica.
    """

    @staticmethod
    def crear_casino(place_data: PlaceIn, actor: str = "system") -> PlaceOut:
        """Crea un casino (usa la capa de storage existente)."""
        # Reusar la lógica existente en PlaceStorage/PlaceDomain
        created = PlaceStorage.create_place(
            nombre=place_data.nombre,
            direccion=place_data.direccion,
            codigo_casino=place_data.codigo_casino,
            ciudad=place_data.ciudad,
            created_by=actor,
        )

        return PlaceOut(**created)

    @staticmethod
    def modificar_casino(casino_id: int, cambios: dict, actor: str = "system") -> dict:
        """
        Modifica los campos editables de un casino.

        Reglas:
        - No se permite modificar `codigo_casino` (si viene en `cambios` y difiere, se lanza ValueError).
        - Si se cambia `nombre`, debe ser único (case-insensitive) entre los demás casinos.

        Retorna el dict actualizado del casino.
        Lanza KeyError si el casino no existe, ValueError para violaciones de negocio.
        """

        # Asegurar CSV
        PlaceStorage._ensure_csv_exists()

        # Leer CSV
        df = pd.read_csv(PLACES_CSV)

        # Verificar existencia
        if df.empty or int(casino_id) not in df['id'].astype(int).values:
            raise KeyError(f"No existe un casino con ID {casino_id}")

        # Obtener fila actual
        row_idx = df.index[df['id'].astype(int) == int(casino_id)][0]
        current = df.loc[row_idx].to_dict()

        # Validar codigo_casino inmutable
        if 'codigo_casino' in cambios:
            nueva = str(cambios['codigo_casino']).strip().upper()
            actual = str(current.get('codigo_casino', '')).strip().upper()
            if nueva != actual:
                raise ValueError('El código del casino no puede ser modificado')

        # Validar nombre único si se intenta cambiar
        if 'nombre' in cambios:
            nuevo_nombre = str(cambios['nombre']).strip()
            # usar helper del repo para comprobar existencias excluyendo este id
            if PlaceStorage.existe_nombre(nuevo_nombre, exclude_id=int(casino_id)):
                raise ValueError(f"Ya existe otro casino con el nombre '{nuevo_nombre}'")

        # Aplicar cambios permitidos (solo columnas conocidas)
        allowed = {'nombre', 'direccion', 'estado'}
        for k, v in cambios.items():
            if k in allowed:
                df.at[row_idx, k] = v

        # Auditoría
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'updated_at' not in df.columns:
            df['updated_at'] = None
        if 'updated_by' not in df.columns:
            df['updated_by'] = None

        df.at[row_idx, 'updated_at'] = timestamp
        df.at[row_idx, 'updated_by'] = actor

        # Guardar cambios
        df.to_csv(PLACES_CSV, index=False)

        # Devolver fila actualizada como dict
        updated = df.loc[row_idx].fillna('').to_dict()
        return updated

    @staticmethod
    def inactivar_casino(casino_id: int, actor: str = "system") -> bool:
        """Marca un casino como inactivo. Reusa la función de PlaceStorage."""
        return PlaceStorage.inactivar(casino_id, actor=actor)

    @staticmethod
    def listar_maquinas(casino_id: int, only_active: bool = True) -> List[dict]:
        """Devuelve la lista de máquinas asociadas a un casino.

        Usa `MachinesRepo` y filtra por `casino_id` (campo usado en CSV como `casino_id`).
        Si only_active=True, devuelve solo activas.
        Si only_active=False, devuelve solo inactivas.
        """
        machines_repo = MachinesRepo()
        all_machines = machines_repo.list_all()

        result = []
        for m in all_machines:
            # Normalizar id/casino_id
            try:
                m_casino = int(m.get('casino_id') or m.get('place_id') or 0)
            except Exception:
                # si no se puede convertir, saltar
                continue

            if m_casino != int(casino_id):
                continue

            # Determinar si la máquina está activa
            estado = m.get('estado') or m.get('is_active')
            is_machine_active = False
            
            if isinstance(estado, str):
                is_machine_active = estado.strip().lower() in ['true', '1', 'yes', 'y', 't']
            elif isinstance(estado, bool):
                is_machine_active = estado
            elif estado in [1, '1']:
                is_machine_active = True

            # Filtrar según only_active
            if only_active and not is_machine_active:
                continue  # Solo queremos activas, esta es inactiva
            elif not only_active and is_machine_active:
                continue  # Solo queremos inactivas, esta es activa

            result.append(m)

        return result


__all__ = ["CasinoManagement"]

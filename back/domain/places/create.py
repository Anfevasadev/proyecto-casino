# -------------------------------------------
# back/domain/places/create.py
# Función esperada: create_place(data, clock, repo, actor)
#
# Entradas:
#   - data: {name, address?, is_active=True}
#   - clock: hora local
#   - repo: places_repo con helpers: next_id(), existe_name(name), insertar_fila(...)
#   - actor: usuario que opera
#
# Validaciones:
#   - name obligatorio y único (no repetido).
#
# Procesamiento:
#   1) id = next_id()
#   2) Construir fila con auditoría: created_at/by, updated_at/by.
#   3) Guardar.
#
# Salida:
#   - {id, name, address, is_active}
#
# Errores:
#   - Duplicado de name -> ValueError/DomainError.
# -------------------------------------------

from back.storage.place_storage import PlaceStorage
from back.models.place_models import PlaceIn, PlaceOut


class PlaceDomain:
    """Lógica de negocio para casinos"""

    @staticmethod
    def create_place(place_data: PlaceIn, created_by: str = "system") -> PlaceOut:
        """
        Crea un nuevo casino validando las reglas de negocio
        
        Args:
            place_data: Datos del casino a crear
            created_by: Usuario que crea
            
        Returns:
            PlaceOut: Casino creado
            
        Raises:
            ValueError: Si el código ya existe o hay errores
        """
        
        # Crear el casino en el storage
        try:
            created_place_dict = PlaceStorage.create_place(
                nombre=place_data.nombre,
                direccion=place_data.direccion,
                codigo_casino=place_data.codigo_casino,
                created_by=created_by
            )
            
            # Convertir a modelo de salida
            return PlaceOut(**created_place_dict)
            
        except Exception as e:
            raise ValueError(f"Error al crear el casino: {str(e)}")

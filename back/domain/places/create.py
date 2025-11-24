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

from back.storage.places_repo import PlaceStorage
from back.models.places import PlaceIn, PlaceOut


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

        # Validar código único antes de crear
        existing = PlaceStorage.get_place_by_code(place_data.codigo_casino)
        if existing:
            raise ValueError(
                f"Ya existe un casino registrado con el código: {place_data.codigo_casino}"
            )

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

    @staticmethod
    def inactivar_casino(casino_id: int, actor: str = "system") -> bool:
        """
        Desactiva un casino usando la capa de almacenamiento.
        """
        from back.storage.places_repo import PlaceStorage

        try:
            return PlaceStorage.inactivar(casino_id, actor=actor)
        except KeyError as e:
            raise KeyError(str(e))
        except Exception as e:
            raise Exception(f"Error al inactivar casino: {str(e)}")

    @staticmethod
    def update_place(place_id: int, cambios: dict, actor: str = "system") -> dict:
        """
        Actualiza un casino respetando reglas de negocio y delega la persistencia al repo.

        Reglas importantes:
        - `codigo_casino` no puede ser modificado (si viene en `cambios` y difiere, se lanza ValueError).
        - Si se cambia `nombre`, debe ser único (case-insensitive) entre los demás casinos.

        Retorna el dict actualizado.
        """
        # Obtener actual
        existing = PlaceStorage.obtener_por_id(int(place_id))
        if not existing:
            raise KeyError(f"No existe un casino con ID {place_id}")

        # Validar codigo_casino inmutable
        if 'codigo_casino' in cambios:
            nueva = str(cambios['codigo_casino']).strip().upper()
            actual = str(existing.get('codigo_casino', '')).strip().upper()
            if nueva != actual:
                raise ValueError('El código del casino no puede ser modificado')

        # Validar nombre único si se intenta cambiar
        if 'nombre' in cambios:
            nuevo_nombre = str(cambios['nombre']).strip()
            if PlaceStorage.existe_nombre(nuevo_nombre, exclude_id=int(place_id)):
                raise ValueError(f"Ya existe otro casino con el nombre '{nuevo_nombre}'")

        # Delegar la actualización al repo
        try:
            updated = PlaceStorage.actualizar_place(int(place_id), cambios, actor=actor)
            return updated
        except KeyError:
            raise
        except Exception as e:
            raise Exception(f"Error al actualizar casino: {str(e)}")

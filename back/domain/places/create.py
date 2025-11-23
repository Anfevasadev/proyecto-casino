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

from back.storage.place_storage import CasinoStorage
from back.models.place_models import CasinoIn, CasinoOut


class Casino:
    """
    Clase Casino según UML
    Métodos: crearCasino(), modificarCasino(), inactivarCasino(), listarMaquina()
    """

    @staticmethod
    def crearCasino(casino_data: CasinoIn, created_by: str = "system") -> CasinoOut:
        """
        Método crearCasino() según UML
        Crea un nuevo casino validando las reglas de negocio
        
        Args:
            casino_data: Datos del casino a crear (CasinoIn)
            created_by: Usuario que crea
            
        Returns:
            CasinoOut: Casino creado
            
        Raises:
            ValueError: Si el código ya existe o hay errores
        """
        
        # Crear el casino usando el storage
        try:
            created_casino_dict = CasinoStorage.crearCasino(
                nombre=casino_data.nombre,
                direccion=casino_data.direccion,
                codigoCasino=casino_data.codigoCasino,
                created_by=created_by
            )
            
            # Convertir a modelo de salida
            return CasinoOut(**created_casino_dict)
            
        except Exception as e:
            raise ValueError(f"Error al crear el casino: {str(e)}")

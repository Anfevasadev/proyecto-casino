# -------------------------------------------
# back/tests/test_machine_update.py
# Pruebas para la funcionalidad de actualización de máquinas
# -------------------------------------------
import pytest
from back.domain.machines.update import actualizar_maquina, ActualizacionMaquinaError
from back.storage.machines_repo import MachinesRepo
from back.storage.places_repo import PlaceStorage


class MockMachinesRepo:
    """Mock del repositorio de máquinas para pruebas."""
    
    def __init__(self, machines_data=None):
        self.machines_data = machines_data or {}
        self.update_calls = []
    
    def get_by_id(self, machine_id: int):
        return self.machines_data.get(machine_id)
    
    def existe_serial(self, serial: str, exclude_id: int = None):
        for m_id, m in self.machines_data.items():
            if m.get("serial", "").lower() == serial.lower():
                if exclude_id is None or m_id != exclude_id:
                    return True
        return False
    
    def existe_asset(self, asset: str, exclude_id: int = None):
        for m_id, m in self.machines_data.items():
            if m.get("asset", "").lower() == asset.lower():
                if exclude_id is None or m_id != exclude_id:
                    return True
        return False
    
    def actualizar(self, machine_id: int, cambios: dict, actor: str):
        self.update_calls.append((machine_id, cambios, actor))
        machine = self.machines_data.get(machine_id)
        if machine:
            # Simular actualización
            for key, val in cambios.items():
                machine[key] = val
            machine["updated_by"] = actor
            return machine
        return None


class MockPlacesRepo:
    """Mock del repositorio de lugares para pruebas."""
    
    def __init__(self, places_data=None):
        self.places_data = places_data or {}
    
    def obtener_por_id(self, place_id: int):
        # Intentar con int y string
        return self.places_data.get(place_id) or self.places_data.get(str(place_id))


def test_actualizar_maquina_exitosa():
    """Prueba que la actualización básica funciona."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "modelo": "Alpha",
            "serial": "ABC123",
            "asset": "ASS001",
            "denominacion": "100.00",
            "estado": "True",
            "casino_id": "1",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo({
        1: {"id": "1", "nombre": "Casino A", "estado": "True"}
    })
    
    cambios = {
        "marca": "NOVOMATIC",
        "modelo": "Dragon"
    }
    
    resultado = actualizar_maquina(
        machine_id=1,
        cambios=cambios,
        machines_repo=machines_repo,
        places_repo=places_repo,
        actor="admin"
    )
    
    assert resultado["marca"] == "NOVOMATIC"
    assert resultado["modelo"] == "Dragon"
    assert resultado["serial"] == "ABC123"  # No cambió
    assert resultado["denominacion"] == "100.00"  # No cambió


def test_actualizar_maquina_denominacion_prohibida():
    """Prueba que no se puede modificar la denominación."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "modelo": "Alpha",
            "serial": "ABC123",
            "asset": "ASS001",
            "denominacion": "100.00",
            "estado": "True",
            "casino_id": "1",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo()
    
    cambios = {
        "denominacion": "200.00"  # Intento prohibido
    }
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=1,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "denominacion" in str(exc_info.value).lower()


def test_actualizar_maquina_no_existe():
    """Prueba que retorna error si la máquina no existe."""
    machines_repo = MockMachinesRepo()
    places_repo = MockPlacesRepo()
    
    cambios = {"marca": "NOVOMATIC"}
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=999,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "no encontrada" in str(exc_info.value).lower()


def test_actualizar_maquina_serial_duplicado():
    """Prueba que no se permite serial duplicado."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "serial": "ABC123",
            "asset": "ASS001",
            "denominacion": "100.00",
            "created_by": "admin"
        },
        2: {
            "id": "2",
            "marca": "NOVOMATIC",
            "serial": "XYZ789",
            "asset": "ASS002",
            "denominacion": "50.00",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo()
    
    cambios = {
        "serial": "XYZ789"  # Serial que ya existe en máquina 2
    }
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=1,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "serial" in str(exc_info.value).lower()


def test_actualizar_maquina_asset_duplicado():
    """Prueba que no se permite asset duplicado."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "serial": "ABC123",
            "asset": "ASS001",
            "denominacion": "100.00",
            "created_by": "admin"
        },
        2: {
            "id": "2",
            "marca": "NOVOMATIC",
            "serial": "XYZ789",
            "asset": "ASS002",
            "denominacion": "50.00",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo()
    
    cambios = {
        "asset": "ASS002"  # Asset que ya existe en máquina 2
    }
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=1,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "asset" in str(exc_info.value).lower()


def test_actualizar_maquina_casino_inexistente():
    """Prueba que no se permite asignar a un casino que no existe."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "serial": "ABC123",
            "casino_id": "1",
            "denominacion": "100.00",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo()  # Sin casinos
    
    cambios = {
        "casino_id": "999"  # Casino inexistente
    }
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=1,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "casino" in str(exc_info.value).lower() and "no encontrado" in str(exc_info.value).lower()


def test_actualizar_maquina_casino_inactivo():
    """Prueba que no se permite asignar a un casino inactivo."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "serial": "ABC123",
            "casino_id": "1",
            "denominacion": "100.00",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo({
        1: {"id": "1", "nombre": "Casino A", "estado": "True"},
        2: {"id": "2", "nombre": "Casino B", "estado": "False"}  # Inactivo
    })
    
    cambios = {
        "casino_id": "2"  # Casino inactivo
    }
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=1,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "inactivo" in str(exc_info.value).lower()


def test_actualizar_maquina_campos_prohibidos():
    """Prueba que no se pueden modificar campos prohibidos como created_by."""
    machines_repo = MockMachinesRepo({
        1: {
            "id": "1",
            "marca": "IGT",
            "serial": "ABC123",
            "denominacion": "100.00",
            "created_by": "admin"
        }
    })
    places_repo = MockPlacesRepo()
    
    cambios = {
        "created_by": "otro_usuario"  # Campo prohibido
    }
    
    with pytest.raises(ActualizacionMaquinaError) as exc_info:
        actualizar_maquina(
            machine_id=1,
            cambios=cambios,
            machines_repo=machines_repo,
            places_repo=places_repo,
            actor="admin"
        )
    
    assert "created_by" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

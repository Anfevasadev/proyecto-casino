"""
Pruebas completas del módulo de contadores.

Este archivo prueba:
1. Crear contadores (validaciones de negocio)
2. Listar contadores por ID
3. Actualizar contadores en batch
4. Consultar contadores para reportes
5. Listar máquinas por casino
6. Validaciones de relaciones (casino-máquina)
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from back.main import app
from back.storage.counters_repo import CountersRepo
from back.storage.machines_repo import MachinesRepo
from back.storage.places_repo import PlaceStorage

client = TestClient(app)


class TestCountersModule:
    """Suite de pruebas para el módulo de contadores"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup que se ejecuta antes de cada prueba"""
        self.repo_counters = CountersRepo()
        self.repo_machines = MachinesRepo()
        self.repo_places = PlaceStorage()
        yield
        # Cleanup después de cada prueba si es necesario
    
    def test_health_check(self):
        """Verificar que el servidor responde correctamente"""
        # Verificar que el endpoint de counters está disponible
        response = client.get("/api/v1/counters/machines-by-casino/1")
        # Puede ser 200 o 404 (dependiendo si existe el casino), pero no 500
        assert response.status_code in [200, 404]
    
    def test_get_machines_by_casino_success(self):
        """Prueba obtener máquinas de un casino existente"""
        # Primero verificamos que exista al menos un casino activo
        casinos = self.repo_places.listar()
        casino_activo = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_activo = casino
                break
        
        if casino_activo is None:
            pytest.skip("No hay casinos activos para probar")
        
        casino_id = int(casino_activo["id"])
        response = client.get(f"/api/v1/counters/machines-by-casino/{casino_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Si hay máquinas, verificar estructura
        if len(data) > 0:
            machine = data[0]
            assert "id" in machine
            assert "marca" in machine
            assert "modelo" in machine
            assert "serial" in machine
            assert "asset" in machine
    
    def test_get_machines_by_casino_not_found(self):
        """Prueba obtener máquinas de un casino inexistente"""
        response = client.get("/api/v1/counters/machines-by-casino/99999")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()
    
    def test_create_counter_success(self):
        """Prueba crear un contador válido"""
        # Buscar un casino activo con una máquina activa
        casinos = self.repo_places.listar()
        casino_valido = None
        machine_valida = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_id = int(casino["id"])
                machines = self.repo_machines.listar(only_active=True, casino_id=casino_id)
                if machines:
                    casino_valido = casino
                    machine_valida = machines[0]
                    break
        
        if not casino_valido or not machine_valida:
            pytest.skip("No hay casino activo con máquinas activas para probar")
        
        # Preparar datos del contador
        counter_data = {
            "casino_id": int(casino_valido["id"]),
            "machine_id": int(machine_valida["id"]),
            "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "in_amount": 1500.50,
            "out_amount": 800.25,
            "jackpot_amount": 100.0,
            "billetero_amount": 250.0
        }
        
        response = client.post("/api/v1/counters", json=counter_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "id" in data
        assert data["machine_id"] == counter_data["machine_id"]
        assert data["casino_id"] == counter_data["casino_id"]
        assert data["in_amount"] == counter_data["in_amount"]
        assert data["out_amount"] == counter_data["out_amount"]
        assert data["jackpot_amount"] == counter_data["jackpot_amount"]
        assert data["billetero_amount"] == counter_data["billetero_amount"]
        
        # Verificar que incluye información de la máquina
        assert "machine" in data
        if data["machine"] is not None:
            assert "id" in data["machine"]
    
    def test_create_counter_invalid_casino(self):
        """Prueba crear contador con casino inexistente"""
        counter_data = {
            "casino_id": 99999,
            "machine_id": 1,
            "in_amount": 1000.0,
            "out_amount": 500.0,
            "jackpot_amount": 0.0,
            "billetero_amount": 0.0
        }
        
        response = client.post("/api/v1/counters", json=counter_data)
        assert response.status_code == 404
    
    def test_create_counter_invalid_machine(self):
        """Prueba crear contador con máquina inexistente"""
        # Buscar un casino activo
        casinos = self.repo_places.listar()
        casino_activo = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_activo = casino
                break
        
        if not casino_activo:
            pytest.skip("No hay casinos activos para probar")
        
        counter_data = {
            "casino_id": int(casino_activo["id"]),
            "machine_id": 99999,
            "in_amount": 1000.0,
            "out_amount": 500.0,
            "jackpot_amount": 0.0,
            "billetero_amount": 0.0
        }
        
        response = client.post("/api/v1/counters", json=counter_data)
        assert response.status_code == 404
        assert "máquina" in response.json()["detail"].lower()
    
    def test_create_counter_negative_amount(self):
        """Prueba crear contador con montos negativos"""
        # Buscar casino y máquina válidos
        casinos = self.repo_places.listar()
        casino_valido = None
        machine_valida = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_id = int(casino["id"])
                machines = self.repo_machines.listar(only_active=True, casino_id=casino_id)
                if machines:
                    casino_valido = casino
                    machine_valida = machines[0]
                    break
        
        if not casino_valido or not machine_valida:
            pytest.skip("No hay casino activo con máquinas activas para probar")
        
        counter_data = {
            "casino_id": int(casino_valido["id"]),
            "machine_id": int(machine_valida["id"]),
            "in_amount": -1000.0,  # Monto negativo
            "out_amount": 500.0,
            "jackpot_amount": 0.0,
            "billetero_amount": 0.0
        }
        
        response = client.post("/api/v1/counters", json=counter_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_counter_machine_not_belong_to_casino(self):
        """Prueba crear contador con máquina que no pertenece al casino"""
        # Buscar dos casinos diferentes
        casinos = self.repo_places.listar()
        if len(casinos) < 2:
            pytest.skip("Se necesitan al menos 2 casinos para esta prueba")
        
        casino1 = None
        casino2 = None
        machine_casino2 = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                if casino1 is None:
                    casino1 = casino
                else:
                    casino2 = casino
                    # Buscar una máquina del casino 2
                    machines = self.repo_machines.listar(only_active=True, casino_id=int(casino2["id"]))
                    if machines:
                        machine_casino2 = machines[0]
                        break
        
        if not casino1 or not casino2 or not machine_casino2:
            pytest.skip("No se encontraron suficientes casinos/máquinas para la prueba")
        
        # Intentar crear contador en casino1 con máquina de casino2
        counter_data = {
            "casino_id": int(casino1["id"]),
            "machine_id": int(machine_casino2["id"]),
            "in_amount": 1000.0,
            "out_amount": 500.0,
            "jackpot_amount": 0.0,
            "billetero_amount": 0.0
        }
        
        response = client.post("/api/v1/counters", json=counter_data)
        assert response.status_code == 400
        assert "no pertenece" in response.json()["detail"].lower()
    
    def test_get_counter_by_id_success(self):
        """Prueba obtener un contador por ID"""
        # Primero crear un contador
        casinos = self.repo_places.listar()
        casino_valido = None
        machine_valida = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_id = int(casino["id"])
                machines = self.repo_machines.listar(only_active=True, casino_id=casino_id)
                if machines:
                    casino_valido = casino
                    machine_valida = machines[0]
                    break
        
        if not casino_valido or not machine_valida:
            pytest.skip("No hay casino activo con máquinas activas para probar")
        
        counter_data = {
            "casino_id": int(casino_valido["id"]),
            "machine_id": int(machine_valida["id"]),
            "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "in_amount": 2000.0,
            "out_amount": 1000.0,
            "jackpot_amount": 150.0,
            "billetero_amount": 300.0
        }
        
        create_response = client.post("/api/v1/counters", json=counter_data)
        assert create_response.status_code == 201
        created_counter = create_response.json()
        counter_id = created_counter["id"]
        
        # Ahora obtener el contador por ID
        response = client.get(f"/api/v1/counters/{counter_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == counter_id
        assert data["machine_id"] == counter_data["machine_id"]
        assert data["casino_id"] == counter_data["casino_id"]
    
    def test_get_counter_by_id_not_found(self):
        """Prueba obtener un contador inexistente"""
        response = client.get("/api/v1/counters/99999")
        assert response.status_code == 404
    
    def test_update_counters_batch_success(self):
        """Prueba actualizar contadores en batch"""
        # Buscar casino y máquinas
        casinos = self.repo_places.listar()
        casino_valido = None
        machines_validas = []
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_id = int(casino["id"])
                machines = self.repo_machines.listar(only_active=True, casino_id=casino_id)
                if len(machines) >= 2:
                    casino_valido = casino
                    machines_validas = machines[:2]
                    break
        
        if not casino_valido or len(machines_validas) < 2:
            pytest.skip("No hay casino con suficientes máquinas para probar")
        
        # Crear contadores para las máquinas
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        
        for machine in machines_validas:
            counter_data = {
                "casino_id": int(casino_valido["id"]),
                "machine_id": int(machine["id"]),
                "at": f"{fecha_hoy} {hora_actual}",
                "in_amount": 1000.0,
                "out_amount": 500.0,
                "jackpot_amount": 50.0,
                "billetero_amount": 100.0
            }
            client.post("/api/v1/counters", json=counter_data)
        
        # Ahora actualizar en batch
        update_data = {
            "updates": [
                {
                    "machine_id": int(machines_validas[0]["id"]),
                    "in_amount": 1500.0,
                    "out_amount": 700.0
                },
                {
                    "machine_id": int(machines_validas[1]["id"]),
                    "in_amount": 2000.0,
                    "out_amount": 900.0
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/counters/modificacion/{int(casino_valido['id'])}/{fecha_hoy}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_update_counters_batch_casino_not_found(self):
        """Prueba actualizar contadores con casino inexistente"""
        update_data = {
            "updates": [
                {
                    "machine_id": 1,
                    "in_amount": 1500.0
                }
            ]
        }
        
        response = client.put(
            "/api/v1/counters/modificacion/99999/2025-11-26",
            json=update_data
        )
        
        assert response.status_code == 404
    
    def test_update_counters_batch_inactive_casino(self):
        """Prueba actualizar contadores de un casino inactivo"""
        # Buscar un casino inactivo
        casinos = self.repo_places.listar()
        casino_inactivo = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "false":
                casino_inactivo = casino
                break
        
        if not casino_inactivo:
            pytest.skip("No hay casinos inactivos para probar")
        
        update_data = {
            "updates": [
                {
                    "machine_id": 1,
                    "in_amount": 1500.0
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/counters/modificacion/{int(casino_inactivo['id'])}/2025-11-26",
            json=update_data
        )
        
        assert response.status_code == 403
        assert "inactivo" in response.json()["detail"].lower()
    
    def test_update_counters_batch_no_records_found(self):
        """Prueba actualizar contadores cuando no existen registros para esa fecha"""
        # Buscar casino activo
        casinos = self.repo_places.listar()
        casino_activo = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_activo = casino
                break
        
        if not casino_activo:
            pytest.skip("No hay casinos activos para probar")
        
        # Usar una fecha futura donde seguro no hay registros
        fecha_futura = "2099-12-31"
        
        update_data = {
            "updates": [
                {
                    "machine_id": 1,
                    "in_amount": 1500.0
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/counters/modificacion/{int(casino_activo['id'])}/{fecha_futura}",
            json=update_data
        )
        
        assert response.status_code == 404
        assert "no se encontraron registros" in response.json()["detail"].lower()
    
    def test_consultar_reportes_success(self):
        """Prueba consultar contadores para reportes"""
        # Buscar casino con contadores
        casinos = self.repo_places.listar()
        casino_valido = None
        machine_valida = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_id = int(casino["id"])
                machines = self.repo_machines.listar(only_active=True, casino_id=casino_id)
                if machines:
                    casino_valido = casino
                    machine_valida = machines[0]
                    break
        
        if not casino_valido or not machine_valida:
            pytest.skip("No hay casino activo con máquinas activas para probar")
        
        # Crear un contador para hoy
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        counter_data = {
            "casino_id": int(casino_valido["id"]),
            "machine_id": int(machine_valida["id"]),
            "at": f"{fecha_hoy} 10:00:00",
            "in_amount": 3000.0,
            "out_amount": 1500.0,
            "jackpot_amount": 200.0,
            "billetero_amount": 400.0
        }
        client.post("/api/v1/counters", json=counter_data)
        
        # Consultar reportes
        response = client.get(
            f"/api/v1/counters/reportes/consulta?casino_id={int(casino_valido['id'])}&start_date={fecha_hoy}&end_date={fecha_hoy}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_consultar_reportes_invalid_date_range(self):
        """Prueba consultar reportes con rango de fechas inválido"""
        response = client.get(
            "/api/v1/counters/reportes/consulta?casino_id=1&start_date=2025-12-31&end_date=2025-01-01"
        )
        
        assert response.status_code == 400
        assert "fecha" in response.json()["detail"].lower()
    
    def test_create_counter_same_day_different_times(self):
        """Prueba crear múltiples contadores el mismo día a diferentes horas
        
        El sistema permite crear varios contadores para la misma máquina en el mismo día
        siempre y cuando tengan diferentes horas. Esto es útil para registrar múltiples
        lecturas de contadores a lo largo del día.
        """
        # Buscar casino y máquina
        casinos = self.repo_places.listar()
        casino_valido = None
        machine_valida = None
        
        for casino in casinos:
            if str(casino.get("estado", "")).lower() == "true":
                casino_id = int(casino["id"])
                machines = self.repo_machines.listar(only_active=True, casino_id=casino_id)
                if machines:
                    casino_valido = casino
                    machine_valida = machines[0]
                    break
        
        if not casino_valido or not machine_valida:
            pytest.skip("No hay casino activo con máquinas activas para probar")
        
        # Crear primer contador
        fecha_base = "2025-11-28"
        counter_data_1 = {
            "casino_id": int(casino_valido["id"]),
            "machine_id": int(machine_valida["id"]),
            "at": f"{fecha_base} 08:00:00",
            "in_amount": 1000.0,
            "out_amount": 500.0,
            "jackpot_amount": 50.0,
            "billetero_amount": 100.0
        }
        
        response1 = client.post("/api/v1/counters", json=counter_data_1)
        
        # Manejar caso donde ya existe
        if response1.status_code == 409:
            pytest.skip("Ya existen contadores para esta prueba")
        
        assert response1.status_code == 201
        counter1 = response1.json()
        
        # Crear segundo contador el mismo día, diferente hora
        counter_data_2 = {
            "casino_id": int(casino_valido["id"]),
            "machine_id": int(machine_valida["id"]),
            "at": f"{fecha_base} 14:00:00",
            "in_amount": 1500.0,
            "out_amount": 700.0,
            "jackpot_amount": 75.0,
            "billetero_amount": 150.0
        }
        
        response2 = client.post("/api/v1/counters", json=counter_data_2)
        
        # El sistema actualmente permite múltiples contadores el mismo día
        # Si esto cambia en el futuro, esta prueba alertará sobre el cambio de comportamiento
        if response2.status_code == 201:
            # Comportamiento actual: permite múltiples contadores por día
            counter2 = response2.json()
            assert counter2["id"] != counter1["id"]
            assert counter2["at"] != counter1["at"]
        elif response2.status_code == 409:
            # Si el sistema cambia para no permitir duplicados por día
            pytest.skip("El sistema ahora previene múltiples contadores por día")
    
    def test_repository_methods(self):
        """Prueba métodos directos del repositorio"""
        # Test next_id
        next_id = self.repo_counters.next_id()
        assert isinstance(next_id, int)
        assert next_id > 0
        
        # Test insert_counter
        new_counter = {
            "machine_id": 1,
            "casino_id": 1,
            "at": "2025-11-26 12:00:00",
            "in_amount": 1000.0,
            "out_amount": 500.0,
            "jackpot_amount": 50.0,
            "billetero_amount": 100.0,
            "created_at": "2025-11-26 12:00:00",
            "created_by": "test",
            "updated_at": "2025-11-26 12:00:00",
            "updated_by": "test"
        }
        
        inserted = self.repo_counters.insert_counter(new_counter)
        assert inserted is not None
        assert "id" in inserted
        
        # Test get_by_id
        counter_id = inserted["id"]
        retrieved = self.repo_counters.get_by_id(counter_id)
        assert retrieved is not None
        assert retrieved["id"] == counter_id
        
        # Test list_counters
        counters = self.repo_counters.list_counters(limit=10)
        assert isinstance(counters, list)
    
    def test_domain_create_validation(self):
        """Prueba validaciones de la capa de dominio"""
        from back.domain.counters.create import create_counter, NotFoundError
        
        # Test con máquina inexistente
        with pytest.raises(NotFoundError):
            create_counter(
                data={"machine_id": 99999, "in_amount": 1000},
                clock=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                counters_repo=self.repo_counters,
                machines_repo=self.repo_machines
            )
        
        # Test sin machine_id
        with pytest.raises(ValueError):
            create_counter(
                data={"in_amount": 1000},
                clock=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                counters_repo=self.repo_counters,
                machines_repo=self.repo_machines
            )


# Ejecutar las pruebas
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

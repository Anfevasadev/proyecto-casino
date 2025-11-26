from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, status, Body

from back.models.counters import CounterIn, CounterOut, CounterOutWithMachine, MachineSimple, CounterUpdateBatch

from back.domain.counters.create import create_counter, NotFoundError
from back.domain.counters.update import modificar_contadores_batch
from back.domain.counters.read import consultar_contadores_reporte

from back.storage.counters_repo import CountersRepo
from back.storage.machines_repo import MachinesRepo
from back.storage.places_repo import PlaceStorage


# Instancia de repo para máquinas (coherente con otros routers)
repo_counters = CountersRepo()
repo_machines = MachinesRepo()
repo_places = PlaceStorage()

router = APIRouter()


@router.get("/machines-by-casino/{casino_id}", response_model=list[MachineSimple], status_code=status.HTTP_200_OK)
def get_machines_by_casino(casino_id: int = Path(..., ge=1, description="ID del casino")):
	"""
	Obtener todas las máquinas de un casino específico (activas e inactivas).
	Este endpoint se usa antes de crear un contador para seleccionar la máquina.
	"""
	# Validar que el casino existe
	casino = repo_places.obtener_por_id(casino_id)
	if casino is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Casino con id {casino_id} no encontrado")
	
	# Validar que el casino esté activo
	is_active_val = casino.get("estado")
	is_active = str(is_active_val).lower() == "true" if is_active_val else False
	if not is_active:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Casino {casino_id} no está activo")
	
	# Obtener todas las máquinas del casino (activas e inactivas)
	machines = repo_machines.listar(only_active=None, casino_id=casino_id)
	
	if not machines:
		return []
	
	# Convertir a MachineSimple
	result = []
	for m in machines:
		try:
			result.append(MachineSimple(
				id=int(m.get("id")),
				marca=m.get("marca"),
				modelo=m.get("modelo"),
				serial=m.get("serial"),
				asset=m.get("asset"),
			))
		except Exception:
			continue
	
	return result

def local_clock() -> datetime:
    """Reloj local que retorna datetime."""
    return datetime.now()

def _clock_local() -> str:
	"""Reloj local simple: devuelve 'YYYY-MM-DD HH:MM:SS'."""
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@router.get("/{counter_id}", response_model=CounterOut, status_code=status.HTTP_200_OK)
def get_counter(counter_id: int = Path(..., ge=1)):
	"""Obtener un contador por su id."""
	row = repo_counters.get_by_id(counter_id)
	if row is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
	return CounterOut(**row)


@router.post("", response_model=CounterOutWithMachine, status_code=status.HTTP_201_CREATED)

def post_counter(body: CounterIn):
	"""
	Crear un nuevo contador. Valida campos obligatorios y unicidad por casino-fecha-máquina.
	El casino_id debe coincidir con el casino_id de la máquina seleccionada.
	"""
	# Validar que el casino existe
	casino = repo_places.obtener_por_id(body.casino_id)
	if casino is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Casino con id {body.casino_id} no encontrado")
	
	# Validar que el casino esté activo
	is_active_casino = str(casino.get("estado", "")).lower() == "true"
	if not is_active_casino:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Casino {body.casino_id} no está activo")
	
	# Validación explícita en la capa de API: existe la máquina y está activa?
	m_check = repo_machines.get_by_id(int(body.machine_id)) if body.machine_id is not None else None
	if m_check is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Máquina con id {body.machine_id} no encontrada")
	
	is_active_val = m_check.get("is_active") or m_check.get("estado")
	is_active = False
	if isinstance(is_active_val, bool):
		is_active = is_active_val
	elif is_active_val is None:
		is_active = False
	else:
		is_active = str(is_active_val).lower() == "true"
	if not is_active:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Máquina {body.machine_id} no está activa")
	
	# Validar que el casino_id de la máquina coincida con el casino_id enviado
	machine_casino_id = m_check.get("casino_id")
	if machine_casino_id is not None:
		try:
			machine_casino_id = int(float(machine_casino_id))
		except Exception:
			machine_casino_id = None
	
	if machine_casino_id != body.casino_id:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST, 
			detail=f"La máquina {body.machine_id} no pertenece al casino {body.casino_id}"
		)

	# Validar campos obligatorios
	for field in ["in_amount", "out_amount", "jackpot_amount", "billetero_amount"]:
		value = getattr(body, field, None)
		if value is None:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El campo '{field}' es obligatorio.")

	# Validar unicidad: no debe existir ya un registro para casino-fecha-hora-máquina exactos
	# Permite múltiples contadores en el mismo día pero en diferentes horas
	at_completo = body.at if body.at else _clock_local()
	casino_id = body.casino_id
	
	# Buscar si existe un contador con la misma fecha-hora exacta
	existentes = repo_counters.list_counters(
		machine_id=body.machine_id,
		date_from=at_completo,
		date_to=at_completo,
		limit=10
	)
	for ex in existentes:
		# Coincidencia exacta de casino, fecha-hora completa y máquina
		if str(ex.get("casino_id")) == str(casino_id) and str(ex.get("at", "")) == at_completo:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT, 
				detail=f"Ya existe un registro para esta máquina en la fecha-hora {at_completo}. Use una hora diferente."
			)

	try:
		created = create_counter(
			data=body.model_dump(),
			clock=_clock_local,
			counters_repo=repo_counters,
			machines_repo=repo_machines,
			actor="api",
		)
		# Recuperar información básica de la máquina para devolverla junto al contador
		m = repo_machines.get_by_id(created.get("machine_id"))
		machine_simple = None
		if m:
			try:
				machine_simple = MachineSimple(
					id=int(m.get("id")),
					marca=m.get("marca"),
					modelo=m.get("modelo"),
					serial=m.get("serial"),
					asset=m.get("asset"),
				)
			except Exception:
				machine_simple = None
		return CounterOutWithMachine(**{**created, "machine": machine_simple})
	except NotFoundError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/modificacion/{casino_id}/{fecha}", response_model=List[CounterOut])
def modificar_contadores(
    casino_id: int = Path(..., description="ID del Casino"),
    fecha: date = Path(..., description="Fecha de los contadores (YYYY-MM-DD)"),
    payload: CounterUpdateBatch = Body(..., description="Lista de máquinas y sus nuevos valores"),
    actor: str = Query("system", description="Usuario que realiza la modificación")
):
    """
    Actualiza contadores para una lista de máquinas en un Casino y Fecha específicos.
    """
    try:
        return modificar_contadores_batch(
            casino_id=casino_id,
            fecha=fecha,
            batch_data=payload,
            counters_repo=repo_counters,
            places_repo=repo_places,
            clock=local_clock,       
            actor=actor
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}")


@router.get("/reportes/consulta", response_model=List[CounterOut])
def consultar_reportes(
    casino_id: int = Query(..., description="ID del Casino"),
    start_date: date = Query(..., description="Fecha Inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha Fin (YYYY-MM-DD)")
):
    """
    Endpoint para integración con el Módulo de Reportes.
    Filtra registros por rango de fechas y casino.
    """
    try:
        return consultar_contadores_reporte(
            casino_id=casino_id,
            start_date=start_date,
            end_date=end_date,
            counters_repo=repo_counters
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}")
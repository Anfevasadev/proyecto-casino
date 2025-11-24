from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, status

from back.models.counters import CounterIn, CounterOut, CounterOutWithMachine, MachineSimple, CounterUpdateBatch

from back.domain.counters.create import create_counter, NotFoundError
from back.domain.counters.update import modificar_contadores_batch
from back.domain.counters.read import consultar_contadores_reporte

from back.storage.counters_repo import CountersRepo
from back.storage.machines_repo import MachinesRepo
from back.storage.place_repo import PlaceStorage


# Instancia de repo para máquinas (coherente con otros routers)
repo_counters = CountersRepo()
repo_machines = MachinesRepo()
repo_places = PlaceStorage()

router = APIRouter()

def local_clock() -> datetime:
    """Reloj local que retorna datetime."""
    return datetime.now()

def _clock_local() -> str:
	"""Reloj local simple: devuelve 'YYYY-MM-DD HH:MM:SS'."""
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@router.get("", response_model=list[CounterOut], status_code=status.HTTP_200_OK)
def list_counters(
	machine_id: int | None = Query(None, ge=1),
	date_from: str | None = Query(None),
	date_to: str | None = Query(None),
	limit: int = Query(100, ge=1, le=1000),
	offset: int = Query(0, ge=0),
	sort_by: str = Query("at"),
	ascending: bool = Query(True),
):
	"""
	Endpoint para listar contadores.
	"""
	results = repo_counters.list_counters(
		machine_id=machine_id,
		date_from=date_from,
		date_to=date_to,
		limit=limit,
		offset=offset,
		sort_by=sort_by,
		ascending=ascending,
	)
	# mapear a CounterOut (FastAPI/Pydantic hará validación ligera)
	return [CounterOut(**r) for r in results]


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
	Crear un nuevo contador. Delegamos reglas de negocio a `create_counter`.
	Se usa `repo_counters` y `repo_machines` directamente (patrón simple del proyecto).
	"""
	# Validación explícita en la capa de API: existe la máquina y está activa?
	m_check = repo_machines.get_by_id(int(body.machine_id)) if body.machine_id is not None else None
	if m_check is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Máquina con id {body.machine_id} no encontrada")
	# También validar estado activo (coincide con la validación en domain pero repetimos
	# aquí para dar feedback inmediato desde la API)
	is_active_val = m_check.get("is_active")
	is_active = False
	if isinstance(is_active_val, bool):
		is_active = is_active_val
	elif is_active_val is None:
		is_active = False
	else:
		is_active = str(is_active_val).lower() == "true"

	if not is_active:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Máquina {body.machine_id} no está activa")

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
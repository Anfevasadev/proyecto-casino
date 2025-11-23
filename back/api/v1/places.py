from fastapi import APIRouter, HTTPException, status
import csv
import os

router = APIRouter()
CSV_PATH = "./data/casinos.csv"


# Función para leer CSV
def leer_casinos():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# Función para guardar CSV
def guardar_casinos(lista):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nombre", "direccion", "codigoCasino", "estado"])
        for c in lista:
            writer.writerow([c["id"], c["nombre"], c["direccion"], c["codigoCasino"], c["estado"]])


# ------------------------------------------------------------
# GET /casinos  -> listar todos
# ------------------------------------------------------------
@router.get("/casinos")
def listar_casinos():
    return leer_casinos()


# ------------------------------------------------------------
# GET /casinos/{casino_id}
# ------------------------------------------------------------
@router.get("/casinos/{casino_id}")
def obtener_casino(casino_id: int):

    casinos = leer_casinos()

    for c in casinos:
        if int(c["id"]) == casino_id:
            return c

    raise HTTPException(status_code=404, detail="Casino no encontrado")


# ------------------------------------------------------------
# POST /casinos  -> crear casino
# ------------------------------------------------------------
@router.post("/casinos", status_code=201)
def crear_casino(data: dict):

    # Validación 
    if "nombre" not in data or "direccion" not in data or "codigoCasino" not in data:
        raise HTTPException(status_code=400, detail="Faltan campos obligatorios")

    casinos = leer_casinos()

    # Validar códigoCasino único
    for c in casinos:
        if c["codigoCasino"] == data["codigoCasino"]:
            raise HTTPException(status_code=400, detail="El códigoCasino ya existe")

    nuevo_id = len(casinos) + 1

    nuevo = {
        "id": str(nuevo_id),
        "nombre": data["nombre"],
        "direccion": data["direccion"],
        "codigoCasino": data["codigoCasino"],
        "estado": "True"   # siempre se crea activo
    }

    casinos.append(nuevo)
    guardar_casinos(casinos)

    return nuevo


# ------------------------------------------------------------
# PUT /casinos/{casino_id}  -> modificar casino
# ------------------------------------------------------------
@router.put("/casinos/{casino_id}")
def actualizar_casino(casino_id: int, data: dict):

    casinos = leer_casinos()
    encontrado = False

    # Validar códigoCasino duplicado si viene en el body
    if "codigoCasino" in data:
        for c in casinos:
            if c["codigoCasino"] == data["codigoCasino"] and int(c["id"]) != casino_id:
                raise HTTPException(status_code=400, detail="codigoCasino ya está en uso")

    for c in casinos:
        if int(c["id"]) == casino_id:

            # Actualizar solo lo que envían
            if "nombre" in data:
                c["nombre"] = data["nombre"]
            if "direccion" in data:
                c["direccion"] = data["direccion"]
            if "codigoCasino" in data:
                c["codigoCasino"] = data["codigoCasino"]
            if "estado" in data:
                c["estado"] = str(data["estado"])

            encontrado = True
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail="Casino no encontrado")

    guardar_casinos(casinos)
    return c


# ------------------------------------------------------------
# DELETE /casinos/{casino_id}  -> inactivar casino (estado=False)
# ------------------------------------------------------------
@router.delete("/casinos/{casino_id}")
def eliminar_casino(casino_id: int):

    casinos = leer_casinos()

    for c in casinos:
        if int(c["id"]) == casino_id:
            c["estado"] = "False"   # borrado lógico
            guardar_casinos(casinos)
            return {"deleted": True, "id": casino_id}

    raise HTTPException(status_code=404, detail="Casino no encontrado")

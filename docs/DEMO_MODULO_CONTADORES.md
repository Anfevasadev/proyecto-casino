# 📋 GUÍA DE DEMOSTRACIÓN - MÓDULO DE CONTADORES

## 🎯 Objetivo
Demostrar el funcionamiento completo del módulo de contadores, incluyendo la creación, consulta, actualización y generación de reportes.

---

## 📦 PREPARACIÓN INICIAL

### 1. Verificar que el Backend esté Corriendo

```bash
# Terminal 1: Iniciar el backend
cd /workspaces/proyecto-casino2
uvicorn back.main:app --reload --host 0.0.0.0 --port 8000
```

**Verificación esperada:**
- ✅ Servidor corriendo en `http://localhost:8000`
- ✅ Mensaje: "Application startup complete"

### 2. Verificar que el Frontend esté Corriendo

```bash
# Terminal 2: Iniciar el frontend
cd /workspaces/proyecto-casino2/front
npm run dev
```

**Verificación esperada:**
- ✅ Servidor corriendo en `http://localhost:5173`
- ✅ Mensaje: "Local: http://localhost:5173/"

### 3. Verificar Datos Iniciales

```bash
# Verificar que existan casinos activos
cat data/places.csv | head -5

# Verificar que existan máquinas activas
cat data/machines.csv | head -5
```

---

## 🧪 PARTE 1: PRUEBAS AUTOMÁTICAS

### Ejecutar Suite de Pruebas Completa

```bash
cd /workspaces/proyecto-casino2
python -m pytest back/tests/test_counters_module.py -v
```

**Resultado esperado:**
```
==================== 18 passed, 1 skipped ====================
```

**¿Qué verifica esto?**
- ✅ Todos los endpoints funcionan correctamente
- ✅ Las validaciones de negocio están activas
- ✅ Las relaciones entre entidades funcionan
- ✅ El repositorio guarda y recupera datos correctamente

---

## 🌐 PARTE 2: PRUEBAS CON LA API (Postman/Thunder Client)

### 2.1. Listar Máquinas de un Casino

**Endpoint:** `GET /api/v1/counters/machines-by-casino/{casino_id}`

**Paso a paso:**

1. Abrir Postman o Thunder Client
2. Crear nueva petición GET
3. URL: `http://localhost:8000/api/v1/counters/machines-by-casino/1`
4. Enviar petición

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "marca": "IGT",
    "modelo": "S2000",
    "serial": "SN001",
    "asset": "A001"
  },
  {
    "id": 2,
    "marca": "Aristocrat",
    "modelo": "MK6",
    "serial": "SN002",
    "asset": "A002"
  }
]
```

**Validaciones:**
- ✅ Status Code: 200
- ✅ Retorna array de máquinas
- ✅ Cada máquina tiene: id, marca, modelo, serial, asset

**Caso de error (casino inexistente):**

```http
GET http://localhost:8000/api/v1/counters/machines-by-casino/99999
```

**Respuesta esperada:**
```json
{
  "detail": "Casino con id 99999 no encontrado"
}
```
- ✅ Status Code: 404

---

### 2.2. Crear un Contador

**Endpoint:** `POST /api/v1/counters`

**Paso a paso:**

1. Crear nueva petición POST
2. URL: `http://localhost:8000/api/v1/counters`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):

```json
{
  "casino_id": 1,
  "machine_id": 1,
  "at": "2025-11-26 10:00:00",
  "in_amount": 15000.50,
  "out_amount": 8500.25,
  "jackpot_amount": 250.00,
  "billetero_amount": 1200.00
}
```

5. Enviar petición

**Respuesta esperada:**
```json
{
  "id": 1,
  "machine_id": 1,
  "casino_id": 1,
  "at": "2025-11-26 10:00:00",
  "in_amount": 15000.5,
  "out_amount": 8500.25,
  "jackpot_amount": 250.0,
  "billetero_amount": 1200.0,
  "machine": {
    "id": 1,
    "marca": "IGT",
    "modelo": "S2000",
    "serial": "SN001",
    "asset": "A001"
  }
}
```

**Validaciones:**
- ✅ Status Code: 201 Created
- ✅ Retorna ID del contador creado
- ✅ Incluye información de la máquina
- ✅ Todos los montos coinciden

**Casos de error a probar:**

a) **Casino inexistente:**
```json
{
  "casino_id": 99999,
  "machine_id": 1,
  "in_amount": 1000.0,
  "out_amount": 500.0,
  "jackpot_amount": 0.0,
  "billetero_amount": 0.0
}
```
- ✅ Status Code: 404
- ✅ Mensaje: "Casino con id 99999 no encontrado"

b) **Máquina inexistente:**
```json
{
  "casino_id": 1,
  "machine_id": 99999,
  "in_amount": 1000.0,
  "out_amount": 500.0,
  "jackpot_amount": 0.0,
  "billetero_amount": 0.0
}
```
- ✅ Status Code: 404
- ✅ Mensaje contiene "máquina"

c) **Montos negativos:**
```json
{
  "casino_id": 1,
  "machine_id": 1,
  "in_amount": -1000.0,
  "out_amount": 500.0,
  "jackpot_amount": 0.0,
  "billetero_amount": 0.0
}
```
- ✅ Status Code: 422 Validation Error

d) **Máquina de otro casino:**
```json
{
  "casino_id": 1,
  "machine_id": 5,  // Supongamos que esta máquina es del casino 2
  "in_amount": 1000.0,
  "out_amount": 500.0,
  "jackpot_amount": 0.0,
  "billetero_amount": 0.0
}
```
- ✅ Status Code: 400
- ✅ Mensaje: "La máquina X no pertenece al casino Y"

---

### 2.3. Consultar un Contador por ID

**Endpoint:** `GET /api/v1/counters/{counter_id}`

**Paso a paso:**

1. Crear nueva petición GET
2. URL: `http://localhost:8000/api/v1/counters/1`
3. Enviar petición

**Respuesta esperada:**
```json
{
  "id": 1,
  "machine_id": 1,
  "casino_id": 1,
  "at": "2025-11-26 10:00:00",
  "in_amount": 15000.5,
  "out_amount": 8500.25,
  "jackpot_amount": 250.0,
  "billetero_amount": 1200.0
}
```

**Validaciones:**
- ✅ Status Code: 200
- ✅ Retorna el contador solicitado

**Caso de error:**
```http
GET http://localhost:8000/api/v1/counters/99999
```
- ✅ Status Code: 404

---

### 2.4. Actualizar Contadores en Batch

**Endpoint:** `PUT /api/v1/counters/modificacion/{casino_id}/{fecha}`

**Paso a paso:**

1. Primero crear varios contadores para el mismo día:

```bash
# Contador para máquina 1
POST http://localhost:8000/api/v1/counters
{
  "casino_id": 1,
  "machine_id": 1,
  "at": "2025-11-26 08:00:00",
  "in_amount": 10000.0,
  "out_amount": 5000.0,
  "jackpot_amount": 100.0,
  "billetero_amount": 500.0
}

# Contador para máquina 2
POST http://localhost:8000/api/v1/counters
{
  "casino_id": 1,
  "machine_id": 2,
  "at": "2025-11-26 08:00:00",
  "in_amount": 12000.0,
  "out_amount": 6000.0,
  "jackpot_amount": 150.0,
  "billetero_amount": 600.0
}
```

2. Ahora actualizar ambos en batch:

**Petición PUT:**
```http
PUT http://localhost:8000/api/v1/counters/modificacion/1/2025-11-26
Content-Type: application/json

{
  "updates": [
    {
      "machine_id": 1,
      "in_amount": 15000.0,
      "out_amount": 7000.0
    },
    {
      "machine_id": 2,
      "in_amount": 18000.0,
      "out_amount": 9000.0
    }
  ]
}
```

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "machine_id": 1,
    "casino_id": 1,
    "at": "2025-11-26 08:00:00",
    "in_amount": 15000.0,
    "out_amount": 7000.0,
    "jackpot_amount": 100.0,
    "billetero_amount": 500.0
  },
  {
    "id": 2,
    "machine_id": 2,
    "casino_id": 1,
    "at": "2025-11-26 08:00:00",
    "in_amount": 18000.0,
    "out_amount": 9000.0,
    "jackpot_amount": 150.0,
    "billetero_amount": 600.0
  }
]
```

**Validaciones:**
- ✅ Status Code: 200
- ✅ Retorna array con los contadores actualizados
- ✅ Los valores fueron modificados correctamente

**Casos de error a probar:**

a) **Casino inexistente:**
```http
PUT http://localhost:8000/api/v1/counters/modificacion/99999/2025-11-26
```
- ✅ Status Code: 404

b) **Casino inactivo:**
```http
PUT http://localhost:8000/api/v1/counters/modificacion/2/2025-11-26
# (Asumiendo que casino 2 está inactivo)
```
- ✅ Status Code: 403
- ✅ Mensaje contiene "inactivo"

c) **Fecha sin registros:**
```http
PUT http://localhost:8000/api/v1/counters/modificacion/1/2099-12-31
```
- ✅ Status Code: 404
- ✅ Mensaje: "No se encontraron registros"

---

### 2.5. Consultar Contadores para Reportes

**Endpoint:** `GET /api/v1/counters/reportes/consulta`

**Paso a paso:**

1. Crear nueva petición GET
2. URL con parámetros: 
```http
GET http://localhost:8000/api/v1/counters/reportes/consulta?casino_id=1&start_date=2025-11-26&end_date=2025-11-26
```

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "machine_id": 1,
    "casino_id": 1,
    "at": "2025-11-26 08:00:00",
    "in_amount": 15000.0,
    "out_amount": 7000.0,
    "jackpot_amount": 100.0,
    "billetero_amount": 500.0
  },
  {
    "id": 2,
    "machine_id": 2,
    "casino_id": 1,
    "at": "2025-11-26 08:00:00",
    "in_amount": 18000.0,
    "out_amount": 9000.0,
    "jackpot_amount": 150.0,
    "billetero_amount": 600.0
  }
]
```

**Validaciones:**
- ✅ Status Code: 200
- ✅ Retorna todos los contadores del rango de fechas
- ✅ Filtrados por casino_id

**Caso de error (rango inválido):**
```http
GET http://localhost:8000/api/v1/counters/reportes/consulta?casino_id=1&start_date=2025-12-31&end_date=2025-01-01
```
- ✅ Status Code: 400
- ✅ Mensaje contiene "fecha"

---

## 🎨 PARTE 3: PRUEBAS CON EL FRONTEND

### 3.1. Acceder a la Aplicación

1. Abrir navegador
2. Ir a: `http://localhost:5173`
3. Hacer login con credenciales de administrador

**Validaciones:**
- ✅ Página de login se carga correctamente
- ✅ Inicio de sesión exitoso
- ✅ Redirección al dashboard

---

### 3.2. Seleccionar Casino

1. En el dashboard, buscar sección de casinos
2. Seleccionar un casino activo (ej: "Casino Principal")
3. Click en "Ver Máquinas" o similar

**Validaciones:**
- ✅ Se muestra lista de máquinas del casino
- ✅ Solo aparecen máquinas activas
- ✅ Información completa de cada máquina

---

### 3.3. Crear Contador desde UI

1. Seleccionar una máquina
2. Click en "Registrar Contador" o similar
3. Completar formulario:
   - **Fecha/Hora:** 2025-11-26 14:00:00
   - **IN Amount:** 20000.00
   - **OUT Amount:** 12000.00
   - **Jackpot:** 300.00
   - **Billetero:** 1500.00
4. Click en "Guardar"

**Validaciones:**
- ✅ Mensaje de éxito
- ✅ Contador aparece en la lista
- ✅ Datos coinciden con lo ingresado

---

### 3.4. Ver Detalles de un Contador

1. En la lista de contadores
2. Click en un contador específico
3. Verificar que se muestran todos los detalles

**Validaciones:**
- ✅ Modal o página de detalles se abre
- ✅ Información completa del contador
- ✅ Información de la máquina asociada

---

### 3.5. Modificar Contadores (Batch)

1. Ir a vista de "Modificación de Contadores"
2. Seleccionar casino y fecha
3. Click en "Buscar" o "Cargar"
4. Se muestran todos los contadores de ese día
5. Modificar valores de varios contadores
6. Click en "Guardar Cambios"

**Validaciones:**
- ✅ Se cargan todos los contadores del día
- ✅ Se pueden editar múltiples campos
- ✅ Guardado exitoso
- ✅ Mensaje de confirmación

---

### 3.6. Generar Reporte

1. Ir a sección de "Reportes"
2. Seleccionar:
   - **Casino:** Casino Principal
   - **Fecha Inicio:** 2025-11-26
   - **Fecha Fin:** 2025-11-26
3. Click en "Generar Reporte"

**Validaciones:**
- ✅ Se muestra tabla con contadores
- ✅ Datos filtrados correctamente
- ✅ Posibilidad de exportar (si está implementado)

---

## 🔍 PARTE 4: VERIFICACIÓN DE DATOS

### 4.1. Verificar en CSV

```bash
# Ver últimos registros creados
tail -10 data/counters.csv

# Contar total de registros
wc -l data/counters.csv

# Buscar contadores de un casino específico
grep ",1," data/counters.csv | head -5
```

**Validaciones:**
- ✅ Los contadores creados aparecen en el CSV
- ✅ Formato correcto de las columnas
- ✅ Timestamps correctos

---

### 4.2. Verificar Integridad de Datos

```bash
# Ejecutar script de verificación (si existe)
python -c "
from back.storage.counters_repo import CountersRepo
repo = CountersRepo()
counters = repo.list_counters(limit=5)
for c in counters:
    print(f'ID: {c[\"id\"]}, Machine: {c[\"machine_id\"]}, Casino: {c[\"casino_id\"]}')
"
```

**Validaciones:**
- ✅ Datos se recuperan correctamente
- ✅ Tipos de datos correctos
- ✅ No hay valores nulos inesperados

---

## 🎬 PARTE 5: FLUJO COMPLETO DE DEMOSTRACIÓN

### Escenario: "Día típico en el casino"

**Narrativa:** Mostrar un día completo de operación de contadores

#### 5.1. Apertura del día (8:00 AM)

```json
POST /api/v1/counters
{
  "casino_id": 1,
  "machine_id": 1,
  "at": "2025-11-26 08:00:00",
  "in_amount": 0.0,
  "out_amount": 0.0,
  "jackpot_amount": 0.0,
  "billetero_amount": 0.0
}
```

#### 5.2. Lectura de mediodía (12:00 PM)

```json
POST /api/v1/counters
{
  "casino_id": 1,
  "machine_id": 1,
  "at": "2025-11-26 12:00:00",
  "in_amount": 5000.0,
  "out_amount": 3000.0,
  "jackpot_amount": 100.0,
  "billetero_amount": 500.0
}
```

#### 5.3. Lectura de cierre (20:00 PM)

```json
POST /api/v1/counters
{
  "casino_id": 1,
  "machine_id": 1,
  "at": "2025-11-26 20:00:00",
  "in_amount": 12000.0,
  "out_amount": 7000.0,
  "jackpot_amount": 250.0,
  "billetero_amount": 1200.0
}
```

#### 5.4. Corrección de datos

```http
PUT /api/v1/counters/modificacion/1/2025-11-26
{
  "updates": [
    {
      "machine_id": 1,
      "at": "2025-11-26 12:00:00",
      "in_amount": 5500.0,
      "out_amount": 3200.0
    }
  ]
}
```

#### 5.5. Generar reporte del día

```http
GET /api/v1/counters/reportes/consulta?casino_id=1&start_date=2025-11-26&end_date=2025-11-26
```

---

## ✅ CHECKLIST DE VERIFICACIÓN FINAL

### Backend
- [ ] Servidor corriendo sin errores
- [ ] Todas las pruebas automatizadas pasan
- [ ] Endpoints responden correctamente
- [ ] Validaciones funcionan

### API
- [ ] GET /machines-by-casino funciona
- [ ] POST /counters crea correctamente
- [ ] GET /counters/{id} recupera datos
- [ ] PUT /modificacion actualiza en batch
- [ ] GET /reportes/consulta filtra correctamente

### Validaciones
- [ ] Casino inexistente retorna 404
- [ ] Máquina inexistente retorna 404
- [ ] Montos negativos retornan 422
- [ ] Máquina de otro casino retorna 400
- [ ] Rango de fechas inválido retorna 400
- [ ] Casino inactivo retorna 403

### Frontend (si aplica)
- [ ] Login funciona
- [ ] Listado de casinos se muestra
- [ ] Listado de máquinas se muestra
- [ ] Creación de contador desde UI
- [ ] Visualización de contadores
- [ ] Modificación batch desde UI
- [ ] Generación de reportes

### Datos
- [ ] Contadores se guardan en CSV
- [ ] Formato de datos correcto
- [ ] Auditoría (created_by, updated_by) funciona
- [ ] Relaciones casino-máquina respetadas

---

## 🐛 PROBLEMAS COMUNES Y SOLUCIONES

### Error: "Casino con id X no encontrado"
**Solución:** Verificar que el casino existe en `data/places.csv` y está activo (estado=True)

### Error: "La máquina X no pertenece al casino Y"
**Solución:** Verificar en `data/machines.csv` que el casino_id de la máquina coincide

### Error: Connection refused
**Solución:** Verificar que el backend está corriendo en el puerto 8000

### Error: CORS
**Solución:** Verificar configuración de CORS en `back/main.py`

### CSV vacío o corrupto
**Solución:** 
```bash
# Recrear archivo con headers
echo "id,machine_id,casino_id,at,in_amount,out_amount,jackpot_amount,billetero_amount,created_at,created_by,updated_at,updated_by" > data/counters.csv
```

---

## 📊 MÉTRICAS DE ÉXITO

Una demo exitosa debe cumplir:

- ✅ **100% de pruebas automatizadas pasando**
- ✅ **Todos los endpoints funcionando**
- ✅ **Todas las validaciones activas**
- ✅ **Datos persistidos correctamente**
- ✅ **Frontend integrado (si aplica)**
- ✅ **Sin errores en consola**
- ✅ **Tiempos de respuesta < 500ms**

---

## 📝 NOTAS ADICIONALES

### Para Presentación
1. Preparar datos de ejemplo variados
2. Tener backup del CSV original
3. Probar todo el flujo antes de la demo
4. Preparar casos de error para mostrar validaciones

### Documentación Relacionada
- `back/tests/test_counters_module.py` - Pruebas automatizadas
- `back/api/v1/counters.py` - Endpoints implementados
- `back/domain/counters/` - Lógica de negocio
- `back/storage/counters_repo.py` - Persistencia

---

**Fecha de creación:** 26 de Noviembre, 2025  
**Módulo:** Contadores  
**Versión:** 1.0  
**Estado:** ✅ Listo para Demo

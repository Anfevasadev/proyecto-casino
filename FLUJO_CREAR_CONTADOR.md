# Flujo para Crear un Contador

## Cambios Implementados

Se ha modificado el flujo de creación de contadores para que primero se seleccione el casino y luego las máquinas disponibles de ese casino.

## Nuevo Flujo

### 1. Obtener las máquinas de un casino

**Endpoint:** `GET /api/v1/counters/machines-by-casino/{casino_id}`

**Descripción:** Obtiene todas las máquinas activas de un casino específico.

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/counters/machines-by-casino/1
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "marca": "x",
    "modelo": "y",
    "serial": "1234",
    "asset": "A001"
  },
  {
    "id": 2,
    "marca": "y",
    "modelo": "z",
    "serial": "12345",
    "asset": "A0011"
  }
]
```

### 2. Crear el contador con casino_id y machine_id

**Endpoint:** `POST /api/v1/counters`

**Descripción:** Crea un nuevo contador. Ahora requiere tanto `casino_id` como `machine_id`.

**Body (JSON):**
```json
{
  "casino_id": 1,
  "machine_id": 1,
  "in_amount": 1000.0,
  "out_amount": 800.0,
  "jackpot_amount": 50.0,
  "billetero_amount": 150.0
}
```

**Ejemplo completo:**
```bash
curl -X POST http://localhost:8000/api/v1/counters \
  -H "Content-Type: application/json" \
  -d '{
    "casino_id": 1,
    "machine_id": 1,
    "in_amount": 1000.0,
    "out_amount": 800.0,
    "jackpot_amount": 50.0,
    "billetero_amount": 150.0
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "machine_id": 1,
  "casino_id": 1,
  "at": "2025-11-25 12:00:00",
  "in_amount": 1000.0,
  "out_amount": 800.0,
  "jackpot_amount": 50.0,
  "billetero_amount": 150.0,
  "machine": {
    "id": 1,
    "marca": "x",
    "modelo": "y",
    "serial": "1234",
    "asset": "A001"
  }
}
```

## Validaciones Implementadas

1. **El casino debe existir** - Si el `casino_id` no existe, retorna error 404
2. **El casino debe estar activo** - Si el casino está inactivo, retorna error 400
3. **La máquina debe existir** - Si el `machine_id` no existe, retorna error 404
4. **La máquina debe estar activa** - Si la máquina está inactiva, retorna error 404
5. **La máquina debe pertenecer al casino** - Si la máquina no pertenece al casino especificado, retorna error 400
6. **No duplicados** - No se puede crear un contador duplicado para el mismo casino, máquina y fecha

## Estructura del CSV de Contadores

Los contadores se guardan con la siguiente estructura en `data/counters.csv`:

```
id,machine_id,casino_id,at,in_amount,out_amount,jackpot_amount,billetero_amount,created_at,created_by,updated_at,updated_by
```

El `casino_id` se incluye automáticamente basado en la validación y en la información de la máquina.

## Ejemplo de Uso Completo

### Paso 1: Listar casinos disponibles (opcional)
```bash
curl http://localhost:8000/api/v1/places
```

### Paso 2: Obtener máquinas del casino seleccionado
```bash
curl http://localhost:8000/api/v1/counters/machines-by-casino/1
```

### Paso 3: Crear el contador con la máquina seleccionada
```bash
curl -X POST http://localhost:8000/api/v1/counters \
  -H "Content-Type: application/json" \
  -d '{
    "casino_id": 1,
    "machine_id": 2,
    "in_amount": 5000.0,
    "out_amount": 4200.0,
    "jackpot_amount": 100.0,
    "billetero_amount": 300.0
  }'
```

## Notas Importantes

- El campo `at` (fecha/hora) es **opcional**. Si no se proporciona, se usará la fecha/hora actual del servidor.
- Todos los campos de montos (`in_amount`, `out_amount`, `jackpot_amount`, `billetero_amount`) son **obligatorios** y deben ser >= 0.
- Solo se muestran las máquinas **activas** del casino en el endpoint de consulta.
- La validación asegura que la máquina pertenezca al casino especificado para mantener la integridad de los datos.

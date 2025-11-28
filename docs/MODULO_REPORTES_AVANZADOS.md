# Módulo de Reportes Avanzados - Documentación

## Descripción General

El módulo de reportes avanzados proporciona herramientas completas para el análisis y generación de informes detallados sobre el comportamiento de las máquinas de casino. Permite obtener reportes personalizados con filtros avanzados y exportarlos en múltiples formatos.

---

## Funcionalidades Implementadas

### ✅ 1. Generación de Reportes Personalizados

#### Filtros Avanzados Disponibles

- **Por Casino**: Filtra por un casino específico usando `casino_id`
- **Por Marca**: Filtra máquinas de una marca específica (ej: IGT, Aristocrat)
- **Por Modelo**: Filtra máquinas de un modelo específico (ej: Sphinx, Buffalo)
- **Por Rango de Fechas**: `period_start` y `period_end` (YYYY-MM-DD)

#### Tipos de Reporte

1. **Detallado** (`tipo_reporte=detallado`):
   - Desglose completo por máquina
   - Contadores inicial y final de cada máquina
   - Valores calculados por máquina
   - Totales consolidados

2. **Consolidado** (`tipo_reporte=consolidado`):
   - Solo totales por categoría (IN, OUT, JACKPOT, BILLETERO)
   - Utilidad final calculada
   - Estadísticas generales

3. **Resumen** (`tipo_reporte=resumen`):
   - Estadísticas generales
   - Cantidad de máquinas procesadas
   - Máquinas con/sin datos

---

### ✅ 2. Visualización de Datos

Todos los reportes incluyen:

- **Contadores**: IN, OUT, JACKPOT, BILLETERO
- **Utilidades**: Cálculo neto (IN - (OUT + JACKPOT))
- **Información de Casinos**: Nombre y código
- **Información de Máquinas**: Marca, modelo, serial, asset
- **Estadísticas**: Total de máquinas, procesadas, con/sin datos

---

### ✅ 3. Exportación de Reportes

Los reportes pueden exportarse en:

- **JSON**: Respuesta directa del API (visualización en pantalla)
- **PDF**: Formato profesional para impresión y auditorías
- **Excel**: Para análisis adicionales y manipulación de datos

---

## Endpoints Disponibles

### 1. Reporte con Filtros (JSON)

**Endpoint**: `GET /api/v1/balances/reportes/filtros`

**Parámetros**:
```
period_start: string (requerido) - Fecha inicial (YYYY-MM-DD)
period_end: string (requerido) - Fecha final (YYYY-MM-DD)
casino_id: integer (opcional) - ID del casino
marca: string (opcional) - Marca de máquina
modelo: string (opcional) - Modelo de máquina
tipo_reporte: string (opcional) - Tipo: detallado, consolidado, resumen
```

**Ejemplo de uso**:
```bash
# Reporte detallado de un casino específico
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31&casino_id=1&tipo_reporte=detallado

# Reporte de todas las máquinas IGT sin filtrar por casino
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31&marca=IGT

# Reporte consolidado de máquinas modelo Buffalo
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31&modelo=Buffalo&tipo_reporte=consolidado
```

**Respuesta Ejemplo** (tipo_reporte=detallado):
```json
{
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "filters_applied": {
    "casino_id": 1,
    "marca": null,
    "modelo": null
  },
  "tipo_reporte": "detallado",
  "casinos_included": [
    {
      "casino_id": 1,
      "casino_nombre": "Casino Principal",
      "total_machines": 50
    }
  ],
  "machines_summary": [
    {
      "casino_id": 1,
      "casino_nombre": "Casino Principal",
      "machine_id": 1,
      "machine_marca": "IGT",
      "machine_modelo": "Sphinx",
      "machine_serial": "SN001",
      "machine_asset": "A001",
      "denominacion": 100.0,
      "contador_inicial": {
        "at": "2025-01-01 08:00:00",
        "in_amount": 1000.0,
        "out_amount": 800.0,
        "jackpot_amount": 50.0,
        "billetero_amount": 200.0
      },
      "contador_final": {
        "at": "2025-01-31 23:59:59",
        "in_amount": 5000.0,
        "out_amount": 4000.0,
        "jackpot_amount": 300.0,
        "billetero_amount": 800.0
      },
      "in_total": 400000.0,
      "out_total": 320000.0,
      "jackpot_total": 25000.0,
      "billetero_total": 60000.0,
      "utilidad": 55000.0,
      "has_data": true
    }
  ],
  "category_totals": {
    "in_total": 2000000.0,
    "out_total": 1600000.0,
    "jackpot_total": 120000.0,
    "billetero_total": 300000.0,
    "utilidad_final": 280000.0
  },
  "total_machines": 50,
  "machines_processed": 50,
  "machines_with_data": 48,
  "machines_without_data": 2,
  "generated_at": "2025-01-31 23:59:59",
  "generated_by": "api_user"
}
```

---

### 2. Exportar Reporte a PDF

**Endpoint**: `GET /api/v1/balances/reportes/filtros/pdf`

**Parámetros**: Mismos que el endpoint JSON

**Ejemplo de uso**:
```bash
GET /api/v1/balances/reportes/filtros/pdf?period_start=2025-01-01&period_end=2025-01-31&casino_id=1
```

**Respuesta**: Archivo PDF descargable

**Contenido del PDF**:
- Título del reporte
- Información de filtros aplicados
- Información de casinos incluidos
- Tabla con desglose por máquina (si es detallado)
- Totales por categoría
- Utilidad final
- Estadísticas

---

### 3. Exportar Reporte a Excel

**Endpoint**: `GET /api/v1/balances/reportes/filtros/excel`

**Parámetros**: Mismos que el endpoint JSON

**Ejemplo de uso**:
```bash
GET /api/v1/balances/reportes/filtros/excel?period_start=2025-01-01&period_end=2025-01-31&marca=IGT
```

**Respuesta**: Archivo Excel (.xlsx) descargable

**Contenido del Excel**:
- Hoja 1: Información general y filtros
- Hoja 2: Desglose detallado por máquina (si aplica)
- Hoja 3: Totales y estadísticas
- Formato profesional con colores y bordes

---

## Endpoints Anteriores (Mantenidos)

### Reporte por Casino Específico (JSON)

**Endpoint**: `GET /api/v1/balances/casinos/{place_id}/report`

**Descripción**: Genera un reporte detallado de un casino específico (sin filtros avanzados)

---

### Exportar Reporte de Casino a PDF

**Endpoint**: `GET /api/v1/balances/casinos/{place_id}/report/pdf`

---

### Exportar Reporte de Casino a Excel

**Endpoint**: `GET /api/v1/balances/casinos/{place_id}/report/excel`

---

## Casos de Uso Comunes

### 1. Reporte de todas las máquinas IGT en enero

```bash
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31&marca=IGT&tipo_reporte=detallado
```

### 2. Reporte consolidado de un casino específico

```bash
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31&casino_id=1&tipo_reporte=consolidado
```

### 3. Reporte consolidado de todos los casinos activos

```bash
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31
```

### 4. Exportar a PDF todas las máquinas modelo Buffalo

```bash
GET /api/v1/balances/reportes/filtros/pdf?period_start=2025-01-01&period_end=2025-01-31&modelo=Buffalo
```

### 5. Reporte resumen de un casino

```bash
GET /api/v1/balances/reportes/filtros?period_start=2025-01-01&period_end=2025-01-31&casino_id=1&tipo_reporte=resumen
```

---

## Consideraciones Técnicas

### Cálculo de Utilidades

**Fórmula**: `UTILIDAD = IN - (OUT + JACKPOT)`

- **IN**: Total de dinero ingresado
- **OUT**: Total de dinero pagado
- **JACKPOT**: Total de jackpots pagados
- **BILLETERO**: Se reporta pero no entra en el cálculo de utilidad

### Cálculo por Máquina

Para cada máquina se calcula:
```
TOTAL = (CONTADOR_FINAL - CONTADOR_INICIAL) × DENOMINACION
```

Donde:
- **CONTADOR_INICIAL**: Primer registro de contadores en el periodo
- **CONTADOR_FINAL**: Último registro de contadores en el periodo
- **DENOMINACION**: Valor de denominación de la máquina

---

## Testing

### Pruebas Recomendadas

1. **Validar filtros individuales**:
   - Solo marca
   - Solo modelo
   - Solo casino_id

2. **Validar combinaciones de filtros**:
  - Marca + Modelo
  - Modelo + Casino
  - Marca + Modelo + Casino

3. **Validar tipos de reporte**:
   - Detallado
   - Consolidado
   - Resumen

4. **Validar exportaciones**:
   - PDF con filtros
   - Excel con filtros

5. **Casos extremos**:
   - Sin máquinas en el periodo
  - Sin casinos activos
   - Marca/modelo no existente

---

## Mejoras Futuras Sugeridas

1. **Autenticación**: Obtener el usuario del token JWT en lugar de "api_user"
2. **Paginación**: Para reportes muy grandes
3. **Cache**: Cachear reportes frecuentes
4. **Filtros adicionales**: Por estado de máquina, por rango de utilidad, etc.
5. **Gráficos**: Incluir gráficos en PDF/Excel
6. **Comparativas**: Comparar periodos diferentes
7. **Alertas**: Generar alertas cuando la utilidad sea negativa

---

## Reporte Especial: Reporte por Participación

### Descripción

Este submódulo especializado permite analizar la participación de máquinas o grupos de máquinas dentro del casino, considerando un porcentaje asignado, para determinar el **valor de participación** sobre la utilidad total.

### Funcionalidades

#### 1. Selección de Máquinas

El usuario puede elegir una o varias máquinas específicas proporcionando una lista de IDs:

```json
{
  "machine_ids": [1, 2, 3, 5, 8]
}
```

#### 2. Ingreso del Porcentaje de Participación

Se especifica el porcentaje de participación a considerar (0-100):

```json
{
  "porcentaje_participacion": 30.0
}
```

Por ejemplo, si se asigna un **30%** de participación, el valor de participación se calculará multiplicando la utilidad total por dicho porcentaje.

#### 3. Cálculo y Visualización

El reporte muestra:

**Utilidad Total**: Suma de las utilidades de las máquinas seleccionadas en el rango de fechas definido.

**Valor de Participación**: Se calcula como:

```
VALOR DE PARTICIPACIÓN = UTILIDAD TOTAL × (PORCENTAJE / 100)
```

**Ejemplo de cálculo:**
- Máquinas seleccionadas: 3 máquinas (IDs: 1, 2, 3)
- Utilidad Máquina 1: $500,000
- Utilidad Máquina 2: $300,000
- Utilidad Máquina 3: $200,000
- **Utilidad Total**: $1,000,000
- Porcentaje de Participación: 30%
- **Valor de Participación**: $1,000,000 × 0.30 = **$300,000**

### Endpoints Disponibles

#### 1. Generar Reporte por Participación (JSON)

**Endpoint**: `POST /api/v1/balances/participacion`

**Body**:
```json
{
  "machine_ids": [1, 2, 3],
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "porcentaje_participacion": 30.0
}
```

**Respuesta** (200 OK):
```json
{
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "machines_summary": [
    {
      "machine_id": 1,
      "machine_marca": "IGT",
      "machine_modelo": "Sphinx",
      "machine_serial": "SN001",
      "machine_asset": "A001",
      "casino_id": 1,
      "casino_nombre": "Casino Principal",
      "in_total": 500000.0,
      "out_total": 400000.0,
      "jackpot_total": 20000.0,
      "billetero_total": 50000.0,
      "utilidad": 80000.0,
      "has_data": true
    },
    {
      "machine_id": 2,
      "machine_marca": "Aristocrat",
      "machine_modelo": "Buffalo",
      "machine_serial": "SN002",
      "machine_asset": "A002",
      "casino_id": 1,
      "casino_nombre": "Casino Principal",
      "in_total": 600000.0,
      "out_total": 500000.0,
      "jackpot_total": 30000.0,
      "billetero_total": 60000.0,
      "utilidad": 70000.0,
      "has_data": true
    }
  ],
  "total_machines": 2,
  "machines_processed": 2,
  "machines_with_data": 2,
  "machines_without_data": 0,
  "utilidad_total": 150000.0,
  "porcentaje_participacion": 30.0,
  "valor_participacion": 45000.0,
  "in_total": 1100000.0,
  "out_total": 900000.0,
  "jackpot_total": 50000.0,
  "billetero_total": 110000.0,
  "generated_at": "2025-01-31 23:59:59",
  "generated_by": "api_user"
}
```

#### 2. Exportar Reporte de Participación a PDF

**Endpoint**: `POST /api/v1/balances/participacion/pdf`

**Body**: Mismo que el endpoint JSON

**Respuesta**: Archivo PDF descargable

**Contenido del PDF**:
- Información general (periodo, porcentaje)
- Tabla con desglose de máquinas
- **Utilidad Total** destacada
- **Valor de Participación** resaltado
- Totales por categoría

#### 3. Exportar Reporte de Participación a Excel

**Endpoint**: `POST /api/v1/balances/participacion/excel`

**Body**: Mismo que el endpoint JSON

**Respuesta**: Archivo Excel (.xlsx) descargable

**Contenido del Excel**:
- Hoja 1: Información general y resumen
- Hoja 2: Desglose detallado por máquina
- Hoja 3: Cálculos de participación
- Formato profesional con colores

### Casos de Uso

#### Caso 1: Participación de máquinas de alta rotación

```bash
POST /api/v1/balances/participacion
Content-Type: application/json

{
  "machine_ids": [1, 2, 3, 4, 5],
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "porcentaje_participacion": 25.0
}
```

#### Caso 2: Análisis de participación por zona

```bash
# Seleccionar máquinas de la zona VIP
POST /api/v1/balances/participacion
Content-Type: application/json

{
  "machine_ids": [10, 11, 12, 13],
  "period_start": "2025-02-01",
  "period_end": "2025-02-28",
  "porcentaje_participacion": 40.0
}
```

#### Caso 3: Exportar a PDF para presentación

```bash
POST /api/v1/balances/participacion/pdf
Content-Type: application/json

{
  "machine_ids": [1, 2, 3],
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "porcentaje_participacion": 30.0
}
```

### Validaciones

El módulo incluye validaciones robustas:

1. **IDs de máquinas**: Deben existir y estar activas
2. **Porcentaje**: Debe estar entre 0 y 100
3. **Fechas**: Formato YYYY-MM-DD, fecha inicial ≤ fecha final
4. **Datos**: Al menos una máquina debe tener datos en el periodo

### Beneficios

- **Transparencia**: Cálculo claro y auditable
- **Flexibilidad**: Selección personalizada de máquinas
- **Exportación**: PDF y Excel para análisis y presentaciones
- **Precisión**: Usa los mismos cálculos de utilidad del sistema

---

## Soporte

Para más información sobre el módulo de reportes, consultar:
- `/docs/01_arquitectura.md` - Arquitectura general del sistema
- `/docs/02_modelo_datos.md` - Modelo de datos
- `/docs/03_diagramas_flujo.md` - Diagramas de flujo

---

**Última actualización**: 26 de noviembre de 2025

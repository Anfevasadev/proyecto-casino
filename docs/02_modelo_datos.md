# Modelo de Datos del Sistema — Proyecto Casino

Este documento describe el modelo de datos utilizado por el backend del sistema.  
Toda la información se almacena en archivos **CSV** que actúan como una base de datos ligera.  
Cada archivo representa una tabla con columnas definidas y relaciones entre recursos del sistema.

---

# 1. Resumen general del modelo

El sistema se compone de siete entidades principales:

1. **Usuarios**  
2. **Lugares (Casinos)**  
3. **Máquinas**  
4. **Contadores**  
5. **Balances de máquina**  
6. **Balances de casino**  
7. **Logs (auditoría)**

Las relaciones del sistema son:

- Un **usuario** puede crear, actualizar o eliminar datos del sistema.  
- Un **lugar/casino** puede tener muchas **máquinas**.  
- Una **máquina** puede tener muchos **contadores** y muchos **balances de máquina**.  
- Un **casino** puede tener muchos **balances de casino**.  
- Todas las acciones relevantes generan **logs**.

---

# 2. Descripción y estructura de cada CSV

A continuación se define cada archivo CSV, su propósito y significado de cada columna.

---

## 2.1. `users.csv`
**Contiene todos los usuarios del sistema.**

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único del usuario |
| `username` | Nombre de usuario para login |
| `password` | Contraseña cifrada o en texto según implementación actual |
| `role` | Rol del usuario (admin, operador, auditor, etc.) |
| `is_active` | Indica si la cuenta está activa |
| `is_deleted` | Marca si el usuario fue eliminado lógicamente |
| `created_at` | Fecha y hora de creación |
| `created_by` | Usuario que creó el registro |
| `updated_at` | Última fecha de actualización |
| `updated_by` | Usuario que modificó el registro |
| `deleted_at` | Fecha de eliminación lógica |
| `deleted_by` | Usuario que eliminó la cuenta |

---

## 2.2. `places.csv`
**Almacena los lugares/casinos donde están las máquinas.**

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único del casino |
| `nombre` | Nombre del lugar |
| `direccion` | Dirección física del casino |
| `codigo_casino` | Código interno asignado al casino |
| `estado` | Estado actual (activo, inactivo) |
| `created_at` | Fecha de creación |
| `created_by` | Usuario que registró el casino |
| `updated_at` | Última actualización |
| `updated_by` | Usuario que realizó la modificación |

---

## 2.3. `machines.csv`
**Representa las máquinas de juego instaladas en los casinos.**

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único de la máquina |
| `marca` | Marca del fabricante |
| `modelo` | Modelo de la máquina |
| `serial` | Serial único de identificación |
| `asset` | Código de activo de la máquina |
| `denominacion` | Valor nominal por jugada |
| `estado` | Estado general (activa, inactiva) |
| `casino_id` | Relación con `places.id` |
| `created_at` | Fecha de creación |
| `created_by` | Usuario que creó el registro |
| `updated_at` | Última actualización |
| `updated_by` | Usuario que modificó |
| `is_active` | Estado lógico (activa/inactiva) |

---

## 2.4. `counters.csv`
**Historial de contadores registrados para máquinas.**

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único del contador |
| `machine_id` | Relación con `machines.id` |
| `casino_id` | Relación con `places.id` |
| `at` | Fecha/hora del registro |
| `in_amount` | Contador de entradas acumuladas |
| `out_amount` | Contador de salidas acumuladas |
| `jackpot_amount` | Contador de jackpots acumulados |
| `billetero_amount` | Dinero retirado del billetero |
| `created_at` | Fecha de creación |
| `created_by` | Usuario que registró |
| `updated_at` | Última actualización |
| `updated_by` | Usuario modificador |

---

## 2.5. `machine_balances.csv`
**Balances generados por máquina en un periodo determinado.**

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único |
| `machine_id` | Relación con `machines.id` |
| `period_start` | Inicio del periodo |
| `period_end` | Fin del periodo |
| `in_total` | Total de entrada del periodo |
| `out_total` | Total de salida del periodo |
| `jackpot_total` | Total de jackpots del periodo |
| `billetero_total` | Total retirado del billetero |
| `utilidad_total` | GANANCIA neta del periodo |
| `generated_at` | Fecha de generación del balance |
| `generated_by` | Usuario que generó el balance |
| `locked` | Indica si el balance está cerrado (true/false) |

---

## 2.6. `casino_balances.csv`
**Balance general del casino, sumando todas las máquinas del periodo.**

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador del balance |
| `place_id` | Relación con `places.id` |
| `period_start` | Inicio del periodo |
| `period_end` | Fin del periodo |
| `in_total` | Total de entrada del casino |
| `out_total` | Total de salida |
| `jackpot_total` | Total de jackpots |
| `billetero_total` | Total del billetero |
| `utilidad_total` | Utilidad neta del casino |
| `generated_at` | Fecha de generación |
| `generated_by` | Usuario que generó el balance |
| `locked` | Bloqueo del periodo |

---

## 2.7. `logs.csv`
**Historial de auditoría del sistema.**

| Campo | Descripción |
|-------|-------------|
| `timestamp` | Fecha/hora de la acción |
| `action` | Acción realizada (crear, actualizar, inactivar, login, etc.) |
| `machine_id` | ID de máquina asociada (si aplica) |
| `serial` | Serial registrado (si aplica) |
| `inactivation_token` | Token usado para desactivar (si aplica) |
| `motivo` | Motivo de la acción |
| `actor` | Usuario que ejecutó la acción |
| `note` | Notas adicionales |

---

# 3. Relaciones entre entidades

### Diagrama
 ┌────────────┐        1 ──── N        ┌───────────────┐
 │  places    │────────────────────────▶│   machines    │
 └────────────┘                         └───────────────┘
        ▲                                        ▲
        │                                        │
        │ 1 ──── N                               │ 1 ──── N
        │                                        │
 ┌────────────┐                           ┌───────────────┐
 │casino_bal. │                           │   counters    │
 └────────────┘                           └───────────────┘
                                                ▲
                                                │
                                                │ 1 ──── N
                                                │
                                        ┌───────────────┐
                                        │machine_balance│
                                        └───────────────┘

Usuarios (users.csv) interactúan como:

creadores

modificadores

actores en logs

responsables de balances


---

# 4. Notas importantes del modelo de datos

- Los **IDs** son numéricos y funcionan como llave primaria en cada entidad.
- No existen claves foráneas reales, pero la relación se asegura mediante lógica del backend.
- Los balances dependen de los contadores.
- Los contadores dependen de las máquinas.
- Las máquinas dependen del casino.
- El sistema de logs funciona como elemento transversal.

---

# 5. Conclusión

Este modelo de datos permite un manejo estructurado del backend usando archivos CSV.  
La separación clara por entidades facilita:
- la auditoría  
- la generación de reportes  
- el control de máquinas y casinos  
- la trazabilidad de acciones  

El sistema mantiene integridad mediante validaciones estrictas implementadas en el dominio.




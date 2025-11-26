# Diagramas de Flujo del Sistema (Backend)

Este documento contiene los principales flujos de operación del sistema del proyecto casino.

---

## 1. Flujo de Autenticación (Login)

El proceso de login valida credenciales, genera el token y retorna los datos del usuario autenticado.

       ┌──────────────────────┐
       │ Usuario envía login  │
       │ (username/password)  │
       └───────────┬──────────┘
                   ▼
        ┌─────────────────────┐
        │ Buscar usuario por  │
        │ username en Users   │
        └───────────┬─────────┘
                    ▼
        ┌─────────────────────┐
 ¿Usuario existe y está activo?
        └───────┬─────┬──────┘
                │     │
              Sí      No
                │     │
                │     ▼
                │   ┌───────────────────────┐
                │   │ Retornar error 401    │
                │   └───────────────────────┘
                ▼
   ┌──────────────────────────────┐
   │ Validar contraseña (hash)    │
   └──────────┬──────────┬────────┘
              │          │
             Sí          No
              │          │
              ▼          ▼
 ┌────────────────┐   ┌────────────────────┐
 │ Generar token  │   │ Retornar error 401 │
 └───────┬────────┘   └────────────────────┘
         ▼
┌───────────────────────────────┐
│ Retornar token y datos usuario│
└───────────────────────────────┘

---

## 2. Flujo de Creación de Usuario

     ┌────────────────────────┐
     │ Admin envía datos de   │
     │ creación de usuario    │
     └──────────┬─────────────┘
                ▼
   ┌──────────────────────────┐
   │ Validar que username no  │
   │ exista previamente        │
   └──────────┬───────────────┘
              │
        ¿Existe?
       ┌───┬─────┬──────┐
           │     │
          Sí    No
           │     │
           ▼     ▼
┌────────────────┐ ┌─────────────────────┐
│ Retornar error │ │ Hash password │
└────────────────┘ │ Guardar usuario │
└─────────┬──────────┘
          ▼
┌────────────────────────────────┐
│ Retornar usuario creado OK │
└────────────────────────────────┘


---

## 3. Flujo de Creación de Casino (Place)

     ┌────────────────────────┐
     │ Admin envía datos de   │
     │ creación de casino     │
     └──────────┬─────────────┘
                ▼
   ┌──────────────────────────┐
   │ Validar código de casino │
   │ no repetido              │
   └──────────┬───────────────┘
              │
        ¿Existe?
       ┌───┬─────┬──────┐
           │     │
          Sí    No
           │     │
           ▼     ▼
┌────────────────┐ ┌───────────────────────┐
│ Retornar error │ │ Insertar registro en │
└────────────────┘ │ places.csv / DB │
└─────────┬────────────┘
▼
┌──────────────────────────────────────────┐
│ Retornar casino creado / datos completos │
└──────────────────────────────────────────┘

---

## 4. Flujo de Registro de Máquina

  ┌─────────────────────────────────┐
  │ Admin selecciona casino y envía │
  │ datos de máquina                 │
  └─────────────────┬───────────────┘
                    ▼
     ┌─────────────────────────────┐
     │ Validar serial no repetido  │
     └───────────┬─────────────────┘
                 │
               ¿Existe?
            ┌────┬──────┬────┐
                 │      │
                Sí     No
                 │      │
                 ▼      ▼
    ┌─────────────────┐ ┌──────────────────────┐
    │ Retornar error  │ │ Registrar máquina en  │
    └─────────────────┘ │ machines.csv / DB     │
                        └────────────┬─────────┘
                                     ▼
        ┌────────────────────────────────────────┐
        │ Retornar datos completos de la máquina │
        └────────────────────────────────────────┘


---

## 5. Flujo de Registro de Contadores

     ┌──────────────────────────────────────────┐
     │ Usuario selecciona casino y máquina      │
     │ luego ingresa contadores (in/out/jp/etc) │
     └──────────────────┬───────────────────────┘
                        ▼
       ┌─────────────────────────────────────┐
       │ Verificar que la máquina esté activa │
       └──────────────────┬───────────────────┘
                          │
                     ¿Activa?
             ┌────────┬──────┬────────┐
                      │      │
                     No     Sí
                      │      │
                      ▼      ▼
   ┌────────────────────────┐ ┌──────────────────────────┐
   │ Retornar error         │ │ Registrar contadores en  │
   └────────────────────────┘ │ counters.csv / DB        │
                              └──────────────┬──────────┘
                                             ▼
                 ┌─────────────────────────────────────────────┐
                 │ Registrar log de conteo (logs.csv)          │
                 └───────────────────────┬─────────────────────┘
                                         ▼
                ┌──────────────────────────────────────────────┐
                │ Retornar datos del contador registrado        │
                └──────────────────────────────────────────────┘

---

## 6. Flujo de Generación de Balance por Máquina

      ┌──────────────────────────────────────┐
      │ Usuario solicita generar balance      │
      │ para una máquina                      │
      └───────────────────┬───────────────────┘
                          ▼
     ┌────────────────────────────────────────┐
     │ Obtener contadores del período          │
     └───────────────────┬────────────────────┘
                         ▼
      ┌──────────────────────────────────────┐
      │ Calcular totales (in/out/jp/bill/etc) │
      └───────────────────┬───────────────────┘
                          ▼
       ┌────────────────────────────────────┐
       │ Guardar máquina_balance en CSV/DB  │
       └───────────────────┬────────────────┘
                           ▼
     ┌─────────────────────────────────────────┐
     │ Retornar balance final y utilidad        │
     └─────────────────────────────────────────┘

---

## 7. Flujo de Generación de Balance por Casino (Global)

  ┌─────────────────────────────────────────────────┐
  │ Usuario solicita generar balance global casino   │
  └─────────────────────────┬───────────────────────┘
                            ▼
   ┌─────────────────────────────────────────┐
   │ Reunir balances de todas las máquinas   │
   └──────────────┬──────────────────────────┘
                  ▼
 ┌────────────────────────────────────────────┐
 │ Sumar totales: in/out/jp/bill/utilidad     │
 └──────────────┬─────────────────────────────┘
                ▼
┌───────────────────────────────────────────────────┐
│ Guardar casino_balance en CSV/DB                  │
└──────────────────┬────────────────────────────────┘
                   ▼
┌───────────────────────────────────────────────────┐
│ Retornar balance total del casino                 │
└───────────────────────────────────────────────────┘
# Frontend — Quickstart (React + Vite)

Resumen corto: este documento describe cómo ejecutar y desarrollar el frontend del proyecto Cuadre Casino.

## Requisitos
- Node.js (16+ recomendable)
- npm (o yarn/pnpm)

## Instalación

```bash
cd front/
npm install
```

## Variables de entorno

Usar una variable de entorno para configurar la URL base de las API del backend. Vite expone variables que comienzan con `VITE_`.

Ejemplo: crea `front/.env.local` con:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Esto evita hardcodear URLs y facilita trabajar en múltiples entornos.

## Ejecutar en desarrollo

```bash
npm run dev
```

Accede a la app en `http://localhost:5173` (por defecto).

Si prefieres no usar la variable de entorno, puedes habilitar la proxy en `vite.config.js` para redirigir `/api` hacia `http://localhost:8000` en local.

## Compilar para producción

```bash
npm run build
```

El output queda en `front/dist/` listo para servir.

## Notas de integración con backend

- Asegúrate que el backend FastAPI esté disponible en la URL apuntada por `VITE_API_BASE_URL`.
- Si el backend requiere autenticación, documenta el token/flow en `docs/` (ej. cómo se guarda en localStorage / cómo se refresca).

## Recomendación de cambio en código

En `front/src/api/client.js` recomendamos usar:

```javascript
const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
```

de modo que no haya dependencias a URLs internas del entorno GitHub o remotas.

---

Última actualización: 26/11/2025

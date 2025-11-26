# 1. Introducción Manual de Mantenimiento y Solución de Problemas.

El backend depende de operaciones consistentes sobre archivos CSV, variables de entorno y ejecución bajo Uvicorn/FastAPI.

Este manual detalla:

- Mantenimiento preventivo

- Mantenimiento correctivo

- Diagnóstico de errores comunes

- Limpieza y optimización de datos

- Solución de problemas frecuentes

# 2. Mantenimiento Preventivo

## 2.1. Verificación de la estructura de CSV

Los archivos deben existir dentro de: ``back/data/``

Los CSV requeridos son:

- casino_balances.csv

- counters.csv

- logs.csv

- machine_balances.csv

- machines.csv

- places.csv

- users.csv

Revisar semanalmente:

- Existencia de todos los archivos

- Encabezados correctos

- Ausencia de filas vacías o con columnas incompletas

## 2.2. Respaldo periódico de CSV

Los CSV deben respaldarse manualmente, ya que funcionan como la base de datos del sistema.

Ruta recomendada: ``backups/YYYY-MM-DD/``

Ejemplo: 
```bash
mkdir -p backups/2025-01-15
cp back/data/*.csv backups/2025-01-15/
```

## 2.3. Actualización de dependencias

Ejecutar:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
Esto garantiza que las dependencias del backend estén actualizadas y consistentes.

# 3. Mantenimiento Correctivo

## 3.1. Regenerar CSVs desde cero

Si un CSV se daña o pierde encabezados: ``python init_csvs.py``

Esto vuelve a crear los CSV faltantes con encabezados correctos.

|     Nota: Este comando no sobrescribe archivos existentes, solo crea los que falten.

## 3.2. Reiniciar la API

Luego de aplicar cualquier cambio:

- En el código

- En variables de entorno

- En rutas

- En los CSV

Ejecutar: ``uvicorn back.main:app --reload``

Si el puerto está ocupado:
```bash
kill -9 $(lsof -t -i:8000)
uvicorn back.main:app --reload
```

## 3.3. Problemas de permisos de archivos

Si aparece un error como:
```nginx
Permission denied: 'machines.csv'
```

**En Windows:**

- Cerrar Excel, Notepad, o cualquier app que tenga el archivo abierto

- Verificar permisos del directorio ``back/data/``

**En Linux/macOS:** ``chmod 664 back/data/*.csv``

# 4. Solución de Problemas Comunes
## 4.1. Error: “File not found”

Causas:

- El CSV no existe

- La ruta del ``.env`` es incorrecta

- La carpeta fue movida

Revisar en ``.env``:
```ini
CSV_DIR="./back/data"
```
**Comprobar:**
```ini
ls back/data
```

## 4.2. Error: “CSV has no header”

Usualmente causado por:

- Borrado accidental de encabezados

- Guardado incorrecto del archivo

**Solución:**

- Abrir el CSV

- Restaurar la línea de encabezados correspondiente

- Reiniciar la API

## 4.3. Error: “ValueError: fieldnames do not match”

Sucede cuando las claves enviadas no coinciden con los encabezados del CSV.

Soluciones:

- Asegurar coincidencia exacta de nombres

- Revisar mayúsculas/minúsculas

- Evitar columnas extras

## 4.4. Error: “Port already in use”

Para liberar el puerto: 
```bash
kill -9 $(lsof -t -i:8000)
```

**Reiniciar:**
```bash
uvicorn back.main:app --reload
```

## 4.5. Problemas con autenticación

Causas comunes:

- SECRET_KEY cambiada

- Archivo ``users.csv`` dañado

- Tokens expirados

**Solución rápida:**

Regenerar SECRET_KEY en ``.env``:
```ini
SECRET_KEY="nueva-llave-123"
```

## 4.6. La API no arranca

Pasos sugeridos:

- Revisar la consola de error

- Verificar ``.env``

- Confirmar que CSV_DIR existe

- Abrir CSV y validar encabezados

- Ejecutar:
```bash
pip install -r requirements.txt
```

- Reiniciar API:
```bash
uvicorn back.main:app --reload
```

# 5. Limpieza y Optimización

## 5.1. Compactar CSVs

Si crecen demasiado:

- Archivar registros antiguos

- Mantener solo datos necesarios

## 5.2. Rotación manual del log

Cuando ``logs.csv`` crece demasiado:
```bash
mv back/data/logs.csv back/data/logs_2025-01-05.csv
touch back/data/logs.csv
echo "timestamp,action,machine_id,serial,inactivation_token,motivo,actor,note" > back/data/logs.csv
```

# 6. Preguntas Frecuentes (FAQ)

**¿Qué hago si borro un CSV?**

Regenerarlo:
```bash
python init_csvs.py
```

**¿El sistema soporta base de datos real?**

Sí, pero la versión actual funciona solo con CSV.

**¿Puedo editar CSV con Excel?**

Sí, pero asegúrate de:

- No borrar encabezados

- No agregar comas adicionales

- Guardar como UTF-8

# 7. Contacto y Soporte

Para errores no cubiertos:

- Revisar logs del servidor

- Validar CSVs

- Revisar lógica de FastAPI y rutas

- Confirmar integridad del entorno virtual
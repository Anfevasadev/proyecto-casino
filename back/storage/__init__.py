# -------------------------------------------
# back/storage/__init__.py
# Propósito:
#   - Marcar el paquete "storage" y documentar reglas generales de acceso a datos.
#
# Concepto:
#   - "storage" encapsula TODAS las operaciones de lectura/escritura
#     contra los CSV en /data (nuestra "BD").
#   - La capa "domain" NO debería conocer detalles de pandas ni de rutas
#     de archivos; interactúa con funciones limpias definidas aquí.
#
# Reglas generales:
#   - Usar pandas para cargar/guardar CSV (df = pd.read_csv(...), df.to_csv(...)).
#   - Respetar encabezados definidos para cada archivo (orden y nombres).
#   - Si un CSV no existe, devolver DF vacío con columnas correctas o crearlo.
#   - Todas las escrituras deben preservar el orden de columnas.
#   - IDs son enteros; las funciones "next_id" calculan el siguiente ID.
#   - Las fechas/horas son strings en hora local con formato 'YYYY-MM-DD HH:MM:SS'.
#
# Errores:
#   - Las funciones aquí deben lanzar errores simples (ValueError, FileNotFoundError)
#     cuando corresponda; la capa "domain" decidirá cómo manejarlos.
#
# Concurrencia (nota simple, proyecto académico):
#   - Si dos personas escriben al mismo tiempo puede haber conflictos.
#   - Mantendremos esto simple: preferimos commits/PRs secuenciales.
#   - (Opcional) Se podría implementar un lock de archivo si el curso lo requiere,
#     pero por ahora no.
# -------------------------------------------

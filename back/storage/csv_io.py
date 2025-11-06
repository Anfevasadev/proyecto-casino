# -------------------------------------------
# back/storage/csv_io.py
# Propósito:
#   - Helpers genéricos para leer y escribir CSV con pandas,
#     y utilidades compartidas (ej.: next_id).
#
# Funciones sugeridas:
#   1) read_df(csv_path, expected_columns=None)
#      Entradas:
#        - csv_path: Path al archivo CSV.
#        - expected_columns: lista de nombres de columnas en orden esperado (opcional).
#      Comportamiento:
#        - Si el archivo no existe: devolver DF vacío.
#        - Si existe: leer con pd.read_csv(csv_path).
#        - Si expected_columns viene y el DF no las tiene:
#            * asegurar que el DF tenga esas columnas (agregar faltantes vacías)
#            * reordenar columnas al orden de expected_columns.
#      Salida:
#        - pandas.DataFrame listo para usar.
#
#   2) write_df(csv_path, df, expected_columns=None)
#      Entradas:
#        - csv_path: Path destino.
#        - df: DataFrame a persistir.
#        - expected_columns (opcional): para reordenar columnas antes de guardar.
#      Comportamiento:
#        - Reordenar columnas si se especifica expected_columns.
#        - Guardar con df.to_csv(csv_path, index=False).
#      Salida:
#        - None (efecto: escribe archivo).
#
#   3) ensure_columns(df, columns)
#      Entradas:
#        - df: DataFrame.
#        - columns: lista de nombres esperados.
#      Comportamiento:
#        - Añadir columnas faltantes con valores por defecto (vacío/NaN o False para bool).
#        - Reordenar al final.
#      Salida:
#        - DataFrame con columnas completas y ordenadas.
#
#   4) next_id(df, id_col="id")
#      Entradas:
#        - df: DataFrame; puede estar vacío.
#        - id_col: nombre de la columna ID.
#      Comportamiento:
#        - Si df está vacío o no tiene la columna: retorna 1.
#        - Si tiene datos: castear a int y retornar max + 1.
#      Salida:
#        - int con el siguiente ID disponible.
#
# Notas de tipos:
#   - Forzar tipos al leer (si se requiere) se puede hacer en cada repo; aquí mantener simple.
#   - Manejar strings con .fillna('') cuando sea útil; evitar que NaN suba a la API.
# -------------------------------------------

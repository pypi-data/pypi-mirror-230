import pandas as pd
import pyarrow.parquet as pq
# Leer el archivo Parquet con pandas
parquet ="C:\\Users\\e-ajuareza\\Documents\\Yastas\\yas-cierre-sii\\params\\streaming\\parquet\\trn_streaming_movimientos-00000-of-00001.parquet"
df = pd.read_parquet(parquet)

# Obtener los tipos de datos de cada columna
tipos_de_datos = df.dtypes

# Imprimir los tipos de datos
for columna, tipo_dato in tipos_de_datos.iteritems():
    print(f"Columna: {columna}, Tipo de dato: {tipo_dato}")
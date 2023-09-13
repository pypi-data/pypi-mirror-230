from data_code.gcp.secrets import get_secret
import psycopg2

class Database():
    """_summary_

    Args:
        Proxy (Proxy): _description_
    """
    def __init__(self, host, port, database, secret_user, secret_pswd, project_id):
        self.host = host
        self.port = port
        self.database_name = database
        user = get_secret(secret_user,project_id)
        password = get_secret(secret_pswd,project_id)
        self.user = user
        self.password = password
        
    def get_connection(self):
        # Establecer la conexión con la base de datos
        connection = psycopg2.connect(
            host=self.host,
            port=self.port, 
            database=self.database_name,
            user=self.user,
            password=self.password
        )
        return connection
    
    def get_tables(self, connection):

        # Crear un cursor para ejecutar consultas
        cursor = connection.cursor()
        

        # Obtener los nombres de las tablas
        cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                    """)

        # Obtener los resultados
        filas = cursor.fetchall()

        # Procesar los resultados
        tablen="Tablenames"
        print(f"\n/ {tablen.upper():^20} \\")
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        
        for fila in filas:
            print(f"| {fila[0]:^20} |")
            print("________________________")
        print("\n")
        # Cerrar el cursor y la conexión
        #cursor.close()
        
    def execute_query(self, connection, query:str):

        # Crear un cursor para ejecutar consultas
        cursor = connection.cursor()

        # Ejecutar una consulta de ejemplo
        cursor.execute(query)
        schema = cursor.description

        # Obtener los resultados de la consulta
        query_result = cursor.fetchall()

        # Procesar los resultados
        # for fila in filas:
        #     print(fila)

        # Cerrar el cursor y la conexión
        cursor.close()
        return schema, query_result

    def close_connection(self, connection):
        # Cerrar el cursor y la conexión
        connection.close()
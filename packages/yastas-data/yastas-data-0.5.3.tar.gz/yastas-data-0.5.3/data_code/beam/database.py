import apache_beam as beam
from data_code.gcp.sql import Database
import logging
import time
import os

class Proxy(beam.DoFn):
    """Funcionalidades relacionadas al proxy para lograr comunicación con bases de datos.
    """
    def __init__(self, string_connection):
        self.string_connection = string_connection
        
    def logprint_i(self,msg):
        logging.info(msg)
        print(msg)

    def setup(self):
        self.logprint_i("Inicia levantacion del proxy.....")
        PROXYUP_COMMANDS = [
            f"pwd && rm -fr DTF && mkdir DTF && cd DTF && \
            wget --progress=bar:force:noscroll https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && ls -la cloud_sql_proxy && \
            chmod 755 cloud_sql_proxy && ls -la cloud_sql_proxy && pwd && ls -latrh && \
            nohup ./{self.string_connection} -ip_address_types=PRIVATE  & ",
        ]

        self.logprint_i("Inicia descarga proxy")
        for command in PROXYUP_COMMANDS:
            os.system(command)
            time.sleep(5)
        self.logprint_i("termina levantacion del proxy.....")

        self.logprint_i("proxy_up_executed")
        
    def process(self,element):
        yield element

class DeleteQuery(beam.DoFn):
    def __init__(self, host, port, database, project_id, secret_user, secret_password):
        self.host=host
        self.port=port
        self.database=database
        self.project_id = project_id
        self.secret_user = secret_user
        self.secret_password = secret_password

    def setup(self):
        
        #self.postgres.raise_proxy(self.string_conn)
        pass

    def process(self, element, query):
        try:
            self.postgres = Database(self.host,self.port,self.database,self.secret_user,self.secret_password, self.project_id)
            self.conn = self.postgres.get_connection()

            if type(query) != str:
                query_converted = query.get()
            else:
                query_converted = query
            print(query_converted)
            
            cursor = self.conn.cursor()
            # Ejecutar una consulta de ejemplo
            cursor.execute(query_converted)  
            self.conn.commit()
            self.postgres.close_connection(self.conn)
            print("Delete executed successfully")
            #self.postgres.shut_down_proxy()
        except Exception as e:
            print("Error executing DELETE query:", e)


    def teardown(self):
        # Investigate functionality
        pass

class GetQuery(beam.DoFn):
    def __init__(self, host, port, database, project_id, secret_user, secret_password):
        self.host=host
        self.port=port
        self.database=database
        self.project_id = project_id
        self.secret_user = secret_user
        self.secret_password = secret_password

    def setup(self):
        
        #self.postgres.raise_proxy(self.string_conn)
        pass

    def process(self, element, query):
        self.postgres = Database(self.host,self.port,self.database,self.secret_user,self.secret_password, self.project_id)
        self.conn = self.postgres.get_connection()

        if type(query) != str:
            query_converted = query.get()
        else:
            query_converted = query
        schema, query_result=self.postgres.execute_query(self.conn, query=query_converted)        
        self.postgres.close_connection(self.conn)
        #self.postgres.shut_down_proxy()
        yield schema, query_result
        

    def teardown(self):
        # Investigate functionality
        pass

def insert_into_postgres(data, host, port, database, secret_user, secret_password, project_id):
    try:
        postgres = Database(host, port, database, secret_user, secret_password, project_id)
        conn = postgres.get_connection()
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))

        insert_query = f"INSERT INTO public.cifras ({columns}) VALUES ({values})"
        print(insert_query)
        cursor.execute(insert_query, list(data.values()))
        # Perform your INSERT operation using cursor.execute()
        
        conn.commit()
        print("Table Updated")
    except Exception as e:
        print("Error inserting into PostgreSQL:", e)
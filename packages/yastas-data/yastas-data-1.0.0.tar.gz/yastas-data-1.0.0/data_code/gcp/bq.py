from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from data_code.utils.appearence import highlight_text
from data_code.utils.evaluate import evaluate_response_bq
import subprocess
import json
import ast

def create_or_evaluate_bq_table(table_id:str,trn_parquet:str, delete_columns:str)->dict:
        """Verifica si existe la tabla y extrae los metadatos; en caso de que no exista la crea con base en el parquet de raw.

        Args:
            table (str): Nombre de la tabla.
            raw_parquet (str): Ruta del parquet.

        Returns:
            dict: Diccionario con la metadata de la tabla.
        """
        try:
            client = bigquery.Client()
            client.get_table(table_id.replace(':','.'))  # Make an API request.
            print(f"Table: {highlight_text(table_id, 32)} already exists.")
            
        except NotFound:
            print(f"Table: {highlight_text(table_id,31)} not found. \nCreating it with parquet: {highlight_text(trn_parquet,34)}")
            # In case running in local, set shell=True
            response = subprocess.run(["bq","load","--autodetect","--source_format=PARQUET", table_id, trn_parquet], capture_output=True, text=True, shell=False)
            message = evaluate_response_bq(response,table_id)
            print(message)
            print("Getting metadata")
            if delete_columns != "[]":
                print("Erasing columns")
                delete_columns_processed = ast.literal_eval(delete_columns.replace('"',''))   
                delete_columns_table(table_id,delete_columns_processed)
                print(f"Columns: {delete_columns} erased.")
                # Procesamiento de hom
                print("\Processing hom")
                validate_columns_hom(table_id)

def validate_columns_hom(table_id):
    table_id_hom = table_id.replace('raw','hom').replace('wrk','hom')
    print(f"""
        Comparing Beetween:
          Wrk: {highlight_text(table_id,33)}
          Hom: {highlight_text(table_id_hom,33)}      
        """)
    try:
        metadata_table_bq = get_metadata(table_id)['schema']['fields']
        wrk_json= json.loads(json.dumps(metadata_table_bq,sort_keys=True))
        metadata_table_bq_hom = get_metadata(table_id_hom)['schema']['fields']
        hom_json = json.loads(json.dumps(metadata_table_bq_hom,sort_keys=True))
        for wrk_data in wrk_json:
            wrk_name = wrk_data['name']
            wrk_type = wrk_data['type']                    
            print(wrk_name)
            for hom_data in hom_json:
                hom_name = hom_data['name']
                hom_type = hom_data['type']
                if wrk_name == hom_name and wrk_type != hom_type:
                    print(f"Work: {wrk_data}\nHom: {hom_data}")
                    fix_column_data_type(table_id, wrk_name, hom_data)
                if wrk_name == hom_name and wrk_type == hom_type:
                    print(highlight_text("Nothing to change",34))
            print("------------------")
    except Exception: 
        print(f"{highlight_text(table_id_hom,31)} does not exist")
        print(f"{highlight_text('WARNING',33)}:Verify data types")
        
def delete_columns_table(table_id:str,delete_columns:str):
    project_id = table_id.split(":")[0]
    client = bigquery.Client(project=project_id)
    table_id = table_id.replace(":",".")
    
    for column in delete_columns:
        delete_columns_query = f'''
                                ALTER TABLE {table_id}
                                DROP COLUMN {column}
                                '''
        print(delete_columns_query)
        query_job = client.query(delete_columns_query)
        query_job.result()

def get_metadata(table_id:str)->dict:
    """_summary_

    Args:
        table_id (str): _description_

    Returns:
        dict: _description_
    """
    metadata_table_bq = subprocess.run(["bq","show","--format=prettyjson", table_id], capture_output=True, shell=False).stdout
    metadata_table_bq = ast.literal_eval(metadata_table_bq.decode('UTF-8'))
    return metadata_table_bq

def fix_column_data_type(table_id:str, data_wrk_name:str, data_hom:dict):
    client = bigquery.Client()
    print(f"Fixing field {data_wrk_name}")
    
    table_id = table_id.replace(":",".")
    dropping_query = f"""
                ALTER TABLE {table_id} 
                DROP COLUMN {data_wrk_name};
                """
    print(dropping_query)
    query_job = client.query(dropping_query)
    query_job.result()
    data_type = convert_data_types(data_hom['type'])
    creating_query = f"""
                    ALTER TABLE {table_id} 
                    ADD COLUMN {data_wrk_name} {data_type}
                    """
    if data_hom['description']:
        creating_query = f"{creating_query} OPTIONS (description='{data_hom['description']}');"
    else:
        creating_query += ";"
    
    print(creating_query)
    query_job = client.query(creating_query)
    query_job.result()

def convert_data_types(to_convert:str):
    types = {
        "ARRAY":"ARRAY",
        "BIGNUMERIC":"BIGNUMERIC",
        "BOOL":"BOOL",
        "BYTES":"BYTES",
        "DATE":"DATE",
        "DATETIME":"DATETIME",
        "FLOAT":"FLOAT64",
        "GEOGRAPHY":"GEOGRAPHY",
        "INTEGER":"INT64",
        "INTERVAL":"INTERVAL",
        "JSON":"JSON",
        "NUMERIC":"NUMERIC",
        "STRING":"STRING",
        "STRUCT":"STRUCT",
        "TIME":"TIME",
        "TIMESTAMP":"TIMESTAMP",
    }
    return types[to_convert]

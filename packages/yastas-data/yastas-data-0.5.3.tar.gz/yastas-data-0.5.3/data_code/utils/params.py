import gcsfs
import json

def get_conf_environment(env:str)->tuple:
    """_summary_

    Args:
        env (str): _description_

    Raises:
        KeyError: _description_

    Returns:
        str: _description_
    """

    if env == "dev":
        uri_base = "gs://us-east1-yas-dev-composer-e-edde754f-bucket/data/yas-dwh"
        conf_file = f"{uri_base}/conf.json"
        connections = f"{uri_base}/db_connections.json"

    elif env == "qas":
        uri_base = "gs://us-east1-yas-qas-composer-e-40e740d3-bucket/data/yas-dwh"
        conf_file = f"{uri_base}/conf.json"
        connections = f"{uri_base}/db_connections.json"

    elif env == "int":
        uri_base = "gs://us-east1-yas-int-composer-e-83ac79a1-bucket/data/yas-dwh"
        conf_file = f"{uri_base}/conf.json"
        connections = f"{uri_base}/db_connections.json"

    elif env == "prd":
        uri_base = "gs://us-east1-yas-prd-composer-e-b710217f-bucket/data/yas-dwh"
        conf_file = f"{uri_base}/conf.json"
        connections = f"{uri_base}/db_connections.json"
    else:
        raise KeyError(f"Invalid environment {env}")
    # print("conf: ",conf_file)
    return conf_file,connections

def evaluate_app(app:str)->str:
    """Take in consideration if is necesary to add more information in the app chain.

    Args:
        app (str): Which app es going to work

    Returns:
        str: Chain nedeed in order to access to the elements. (templates, staging, etc.)
    """
    #TODO: If app still have cuentas...
    return app

def get_params(params_file:str, environment:str)->dict:
    """Get information related to each process in the paramaters file.

    Args:
        params_file (str): Uri file with the parameters in JSON format.
        environment (str): Which environment is going to run.

    Returns:
        dict: The whole information needed in order to process dataflow.
    """
    print(f"params:\t{params_file}\nenv:\t{environment}")
    with gcsfs.GCSFileSystem().open(params_file,encoding='utf-8') as parameters:
        jd = json.load(parameters)
        conf_file, connections = get_conf_environment(environment)
        with gcsfs.GCSFileSystem().open(conf_file,encoding='utf-8') as config:
            conf = json.load(config)

            # Datos generales
            service_account_email = conf["service_account_dwh"]
            setup_file = conf["setup_file"]
            runner = conf["runner"]
            region = conf["region"]
            project = conf["proy_dwh"]
            dataset_bq= conf["dataset_l"]

            app = jd['app']
            template_name = jd["template_name"]
            code_file = jd["code_file"]
            config_name = jd["config_file"]


            app = evaluate_app(app)
            uri = f"gs://yas-{environment}-dwh-des/{app}"
            template_location = f"{uri}/tpl/{template_name}"
            config_file = f"{uri}/param/{config_name}"
            staging_location = f"gs://yas-{environment}-dwh-staging/"
            temp_location = f"gs://yas-{environment}-dwh-tmp/"
            print(f'uri:\t{uri}')
                    

            params = {
                "setup_file":setup_file,
                "service_account_email":service_account_email,
                "project":project,
                "runner":runner,
                "region":region,
                "template_location":template_location,
                "config_file":config_file,
                "staging_location":staging_location,
                "temp_location":temp_location,
                "code_file":code_file,
                "dataset_bq":dataset_bq
            }

            if code_file=='./DFC_DWH_BCH_CAN_SQL.py':
                json_file = open("connections/app_database.json", "r").read()
                app_dict = json.loads(json_file)
                database = app_dict[jd['app']]
                print(f"database:\t{database}")
                database_connections = json.load(gcsfs.GCSFileSystem().open(connections,encoding='utf-8'))
                creds = database_connections[database]
                user = creds['user']
                pss = creds['pss']
                psswd = creds['psswd']
                db = creds['dbname']
                host = creds['host']
                port = creds['port']
                database_type = creds['type']
                certs_location = f"{uri}/security/"

                # General
                
                gen = database_connections["General"]
                sslmode = gen["sslmode"]
                sslrootcert = gen["sslrootcert"]
                sslcert = gen["sslcert"]
                sslkey = gen["sslkey"]
                schema = gen["schema"]

                sql_params = {
                    "user":user,
                    "pss":pss,
                    "psswd":psswd,
                    "db":db,
                    "host":host,
                    "port":port,
                    "type":database_type,
                    "certs_location":certs_location,
                    "sslmode": sslmode,
                    "sslrootcert": sslrootcert,
                    "sslcert": sslcert,
                    "sslkey": sslkey,
                    "schema": schema,
                    "app":jd['app']
                }

                params.update(sql_params)

                print(params)
                

    return params
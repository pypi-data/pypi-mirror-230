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
    uri_base = f"gs://yas-{env}-dwh-des/DWH"

    conf_file = f"{uri_base}/conf.json"
    connections = f"{uri_base}/conf_BD.json"

    # print("conf: ",conf_file)
    return conf_file,connections

def evaluate_app(app:str)->str:
    """Take in consideration if is necesary to add more information in the app chain.

    Args:
        app (str): Which app es going to work

    Returns:
        str: Chain nedeed in order to access to the elements. (templates, staging, etc.)
    """

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
                database = jd['app']
                print(f"database:\t{database}")
                database_connections = json.load(gcsfs.GCSFileSystem().open(connections,encoding='utf-8'))
                project_secrets = database_connections['project_secrets']
                creds = database_connections[database]
                print(creds)
                string_connection = creds['string_connection']
                secret_user = creds['secret_username']
                secret_password = creds['secret_password']
                db = creds['database']
                host = creds['hostname']
                port = creds['port']

                # General

                sql_params = {
                    "string_connection":string_connection,
                    "secret_user":secret_user,
                    "secret_password":secret_password,
                    "db":db,
                    "host":host,
                    "port":port,
                    "project_secrets":project_secrets,
                    "app":jd['app']
                }

                params.update(sql_params)

                print(params)

                

    return params
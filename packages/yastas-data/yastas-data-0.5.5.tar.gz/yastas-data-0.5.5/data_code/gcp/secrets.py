from google.cloud import secretmanager

def get_secret(secret:str, project_id:str):
    PROJECT_ID= project_id
    client = secretmanager.SecretManagerServiceClient()

    secret_name = secret

    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode("UTF-8")

    return secret_value
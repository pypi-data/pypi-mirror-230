from data_code.utils.appearence import highlight_text
import subprocess

def evaluate_response(response: subprocess.CompletedProcess) -> str:
    if response.returncode == 0:
        message = "Dataflow template has been created successfully."
    else:
        message = (
            f"It couldn't be completed\n"
            f"It finished with response: {response.returncode}\n"
            f"Command error output:\n\n{highlight_text(response.stderr.decode('utf-8'),31)}"
        )
        raise ValueError(message)
    return message

def evaluate_response_bq(response: subprocess.CompletedProcess, table_id:str) -> str:
    if response.returncode == 0:
        message = f'{highlight_text(table_id, 32)} was created succesfully'
    else:
        message = (
            f"It couldn't be completed\n"
            f"It finished with response: {response.returncode}\n"
            f"Command error output:\n\n{response.stderr}"
            f"Output:\n\n{response.stdout}"
        )
        raise ValueError(message)
    return message
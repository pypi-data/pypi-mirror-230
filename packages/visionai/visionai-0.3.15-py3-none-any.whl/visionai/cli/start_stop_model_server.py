import typer
from rich import print
from rich.console import Console


from util.docker_utils import *

err_console = Console(stderr=True)
models_server_app = typer.Typer()

@models_server_app.command('start')
def model_server_start():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/modelserver/start')
            print(status)
    except Exception as e:
        print(e)


@models_server_app.command('stop')
def model_server_stop():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/modelserver/stop')
            print(status)
    except Exception as e:
        print(e)
import typer
from rich import print
from rich.console import Console


from util.docker_utils import *

err_console = Console(stderr=True)
web_app = typer.Typer()

@web_app.command('start')
def web_app_start():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/webserver/start')
            print(status)
    except Exception as e:
        print(e)


@web_app.command('stop')
def web_app_stop():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/webserver/stop')
            print(status)
    except Exception as e:
        print(e)
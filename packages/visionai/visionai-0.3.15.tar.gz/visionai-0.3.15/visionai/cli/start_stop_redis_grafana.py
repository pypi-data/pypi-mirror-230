import typer
from rich import print
from rich.console import Console


from util.docker_utils import *

err_console = Console(stderr=True)
redis_grafana_app = typer.Typer()

@redis_grafana_app.command('start')
def redis_grafana_start():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/redis_grafana/start')
            print(status)
    except Exception as e:
        print(e)


@redis_grafana_app.command('stop')
def redis_grafana_stop():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/redis_grafana/stop')
            print(status)
    except Exception as e:
        print(e)
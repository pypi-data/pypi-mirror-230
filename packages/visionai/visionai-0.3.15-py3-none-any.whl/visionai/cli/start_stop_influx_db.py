import typer
from rich import print
from rich.console import Console


from util.docker_utils import *

err_console = Console(stderr=True)
influx_db = typer.Typer()

@influx_db.command('start')
def influxdb_start():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/influxdb/start')
            print(status)
    except Exception as e:
        print(e)


@influx_db.command('stop')
def influxdb_stop():
    try:
        from config import check_visionai_api,service_communication,VISIONAI_API_URL
        service_status = check_visionai_api()
        if service_status:
            status = service_communication(f'{VISIONAI_API_URL}/influxdb/stop')
            print(status)
    except Exception as e:
        print(e)
import typer
from rich import print
import docker
from rich.console import Console

import sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from config import *
from util.docker_utils import *
from models.triton_client import TritonClient

err_console = Console(stderr=True)
tc = TritonClient()

def stop_cmd():
    try:
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print(f'Stop web-app....')
        client = docker.from_env()
        web_service_container = client.containers.get(VISIONAI_API_CONTAINER_NAME)
        web_service_container.stop()
    except docker.errors.NotFound :
        message = typer.style(f"Web-app not running", fg=typer.colors.WHITE, bg=typer.colors.RED)
        typer.echo(message)



def print_container_status(container_name, tail):
    try:
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print(f'{container_name} status....')
        client = docker.from_env()
        ctainer = client.containers.get(container_name)
        ctainer_status = typer.style(ctainer.status, fg=typer.colors.WHITE, bg=typer.colors.GREEN)
        typer.echo(f"{container_name}: {ctainer_status}")
        logs = ctainer.logs(tail=tail)
        log_message= logs.decode("utf-8")
        print(log_message)
        web_service_port_message = typer.style(json.dumps(ctainer.ports), fg=typer.colors.WHITE, bg=typer.colors.GREEN)
        typer.echo(web_service_port_message)
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - -')

    except docker.errors.NotFound:
        message = typer.style(f"{container_name} not running", fg=typer.colors.WHITE, bg=typer.colors.RED)
        typer.echo(message)

def status_cmd(
    tail: int = typer.Option(20, help='tail number of lines')
    ):
    print_container_status(WEB_APP_CONTAINER_NAME, tail)
    print_container_status(VISIONAI_API_CONTAINER_NAME, tail)
    print_container_status(REDIS_CONTAINER_NAME, tail)
    print_container_status(GRAFANA_CONTAINER_NAME, tail)
    print_container_status(TRITON_SERVER_CONTAINER_NAME, tail)
    print_container_status(INFLUXDB_CONTAINER_NAME, tail)


def restart_cmd():
    '''
    Restart all services
    with env file
    '''

def register_company_cmd(
        name,
        email,
        phone,
        company):
    '''
    Register for VisionAI Toolkit
    :Todo push this details to visionify license server
    '''
    pass

def update_visionai_images_cmd(service):
    from util.docker_utils import pull_latest_image
    if service == "visionai-web":
        pull_latest_image("visionify/visionai-dashboard")
    elif service == "visionai-inference":
        pull_latest_image("visionify/visionai-api")
    elif service == "visionai-email":
        pull_latest_image("visionify/visionai-email")
    else:
        print("Invalid service name")
        return False
    
    return True



def init_cmd(env,update):
    from config import VISIONAI_API_URL
    try:
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - -')

        # Package dependencies:
        # opencv-python = "^4.6.0"
        # torch = "^1.11.0"
        # torchvision = ">=0.12,<0.15"
        # pandas = "^1.3.5"
        # seaborn = ">=0.11.2,<0.13.0"
        # tritonclient = {extras = ["all"], version = "^2.29.0"}
        check_requirements(['opencv-python', 'torch', 'torchvision', 'pandas', 'seaborn', 'tritonclient[all]'], install=True)

        # Check if already running
        web_app_running = False
        web_api_running = False
        redis_running = False
        grafana_running = False
        triton_running = False
        influxdb_running = False

        client = docker.from_env()
        containers = client.containers.list()
        for container in containers:
            if container.name == VISIONAI_API_CONTAINER_NAME:
                print(f'API server already running at: http://localhost:{VISIONAI_API_PORT}')
                web_api_running = True
            if container.name == WEB_APP_CONTAINER_NAME:
                print(f'Web server already running at: http://localhost:{WEB_APP_PORT}')
                web_app_running = True
            if container.name == REDIS_CONTAINER_NAME:
                print(f'Redis server is at: localhost:{REDIS_SERVER_PORT}')
                redis_running = True
            if container.name == GRAFANA_CONTAINER_NAME:
                print(f'Grafana server is at: http://localhost:{GRAFANA_SERVER_PORT}')
                grafana_running = True
            if container.name == TRITON_SERVER_CONTAINER_NAME:
                print(f'Triton http server is at: {TRITON_HTTP_URL}')
                print(f'Triton grpc server is at: {TRITON_GRPC_URL}')
                print(f'Triton prometheus metrics server is at: {TRITON_METRICS_URL}')
                triton_running = True
            if container.name == INFLUXDB_CONTAINER_NAME:
                print(f'InfluxDB server is at: http://localhost:8086')
                influxdb_running = True
        # If all services are running, return
        if web_app_running and web_api_running and redis_running and grafana_running and triton_running and influxdb_running:
            return

        if web_api_running is False:
            # from config import VISIONAI_API_CONTAINER_NAME, VISIONAI_API_PORT, VISIONAI_API_DOCKER_IMAGE,VISIONAI_API_URL
            print(f'Starting web service API at port {VISIONAI_API_PORT}')

            if sys.platform == 'win32':
                DOCKER_SOCK = '//var/run/docker.sock'
            elif sys.platform == 'darwin':
                DOCKER_SOCK = '/var/run/docker.sock'
            else:
                DOCKER_SOCK = '/var/run/docker.sock'
            
            with open(env) as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('CONFIG'):
                    CONFIG_FOLDER = line.split('=')[1].strip()

            docker_container_start(
                container_name=VISIONAI_API_CONTAINER_NAME,
                image=VISIONAI_API_DOCKER_IMAGE,
                portmap={3002:VISIONAI_API_PORT},
                network_name=DOCKER_NETWORK,
                volmap=[
                    f'{DOCKER_SOCK}:/var/run/docker.sock',
                    f'{env}:/App/.env',
                    f'{CONFIG_FOLDER}:/App/config'
                ],
            )
            print(f'Web service API available at: http://localhost:{VISIONAI_API_PORT}') 



    except Exception as e:
        err_console.print_exception()
        print(f'Error: {e}')



if __name__ == '__main__':
    # init_cmd()
    # stop_cmd()
    status_cmd()

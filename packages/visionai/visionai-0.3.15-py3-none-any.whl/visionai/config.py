import os
import sys
from pathlib import Path
import json
import requests
from rich import print

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # visionai/visionai directory
VISIONAI_WEB = FILE.parents[2]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

# Config file
CONFIG_FOLDER = ROOT / 'config'
CONFIG_FILE = ROOT / 'config' / 'config.json'
# CONFIG_FILE = os.getenv('CONFIG_FILE') if os.getenv('CONFIG_FILE') is not None else Path(VISIONAI_WEB / 'visioniai-dashboard/test/camera.ui/database/database.json')


VISIONAI_API_URL = 'http://localhost:3002'



SCENARIOS_URL = "https://docsvisionify.blob.core.windows.net/docs-images/scenarios.json"
# SCENARIOS_URL = "https://raw.githubusercontent.com/visionify/visionai/main/visionai/scenarios/scenarios.json"
SCENARIOS_OVERRIDE = ROOT / 'config' / 'scenarios-override.jsn'

# Triton server endpoints
TRITON_HTTP_URL = 'http://localhost:8000'
TRITON_GRPC_URL = 'grpc://localhost:8001'
TRITON_METRICS_URL = 'http://localhost:8002/metrics'

TRITON_SERVER_CONTAINER_NAME = 'visionai-triton'
TRITON_SERVER_DOCKER_IMAGE = 'nvcr.io/nvidia/tritonserver:22.12-py3'
TRITON_SERVER_EXEC = 'tritonserver'
TRITON_SERVER_COMMAND = 'tritonserver --model-repository=/models'
TRITON_MODELS_REPO = ROOT / 'models-repo'

# visionai-api
VISIONAI_API_CONTAINER_NAME = 'visionai-api'
VISIONAI_API_DOCKER_IMAGE = 'visionify/visionai-api'
VISIONAI_API_PORT = 3002
VISIONAI_API_URL = f'http://localhost:{VISIONAI_API_PORT}'
VISIONAI_API_MODELS_REPO = ROOT / 'models-repo'
VISIONAI_API_CONFIG_FOLDER = ROOT / 'config'


# Redis server configuration
REDIS_ENABLED = True
REDIS_SERVER_DOCKER_IMAGE = 'redis'
REDIS_SERVER_PORT = 6379
REDIS_CONTAINER_NAME = 'visionai-redis'

# Grafana server configuration
GRAFANA_ENABLED = True
GRAFANA_SERVER_DOCKER_IMAGE = 'grafana/grafana'
GRAFANA_SERVER_PORT = 3003
GRAFANA_CONTAINER_NAME = 'visionai-grafana'
GRAFANA_DATA_DIR = ROOT / 'config' / 'grafana-data'
GRAFANA_PROVISIONING_DIR = ROOT / 'config' / 'grafana-provisioning'

# Web application (front-end)
WEB_APP_DOCKER_IMAGE = 'visionify/visionai-dashboard'
WEB_APP_PORT = 3001
WEB_APP_CONTAINER_NAME = 'visionai-web'

# Web API (back-end)
# WEB_API_DOCKER_IMAGE = 'visionify/visionai-api'
# WEB_API_PORT = 3002
# WEB_API_MODELS_REPO = ROOT / 'models-repo'
# WEB_API_CONFIG_FOLDER = ROOT / 'config'
# WEB_API_CONTAINER_NAME = 'visionai-api'


INFLUXDB_DB_ENABLED = True
INFLUXDB_SERVER_DOCKER_IMAGE = 'influxdb'
INFLUXDB_CONTAINER_NAME = 'visionai-influxdb'
INFLUXDB_ENABLED = True
INFLUXDB_HOST = 'http://localhost'
INFLUXDB_TOKEN = 'visionai'
INFLUXDB_SERVER_PORT = 8086
INFLUXDB_BUCKET = 'visionai'
INFLUXDB_RUNNING = False

ENV_FILE_PATH = '/home/sumanth/Desktop/vision/disting/.env'

# Docker network
DOCKER_NETWORK = 'visionai-network'

# Test stuff
if os.environ.get('VISIONAI_EXEC') == 'visionai':
    VISIONAI_EXEC = 'visionai'
else:
    VISIONAI_EXEC = 'python -m visionai'

def check_visionai_api():
    try:
        resp = requests.get(VISIONAI_API_URL)
        resp.raise_for_status()
        print(resp.json())
        print(f'init(): VisionAI API is running at {VISIONAI_API_URL}')
        return True
    except requests.exceptions.ConnectionError:
        print("VisionAI API Failed to establish a connection to the server. Please check if the server is running and reachable.")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"VisionAI API An HTTP error occurred: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"VisionAI API An error occurred while making the request: {e}")
        return False
    except Exception as e:
        print(f"VisionAI API An unexpected error occurred: {e}")
        return False


def service_communication(url:str):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print("VisionAI API Failed to establish a connection to the server. Please check if the server is running and reachable.")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"VisionAI API An HTTP error occurred: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"VisionAI API An error occurred while making the request: {e}")
        return False
    except Exception as e:
        print(f"VisionAI API An unexpected error occurred: {e}")
        return False
    


def init_config():
    '''
    Set up initial configuration (one-time only)
    '''

    if not os.path.isdir(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER, exist_ok=True)
        print(f'init(): Created config folder: {CONFIG_FOLDER}')

    if not os.path.exists(CONFIG_FILE):
        config_data = {
            'version': '0.1',
            'cameras': []
            }
        # with open(CONFIG_FILE, 'w') as f:
        #     json.dump(config_data, f, indent=4)
        # print(f'init(): Created camera configuration: {CONFIG_FILE}')

    check_visionai_api()

    # if not os.path.isdir(TRITON_MODELS_REPO):
    #     os.makedirs(TRITON_MODELS_REPO, exist_ok=True)
    #     print(f'init(): Created models repo: {TRITON_MODELS_REPO}')


    # if GRAFANA_ENABLED:
    #     if not os.path.isdir(GRAFANA_DATA_DIR):
    #         os.makedirs(GRAFANA_DATA_DIR, exist_ok=True)
    #         print(f'init(): Created Grafana data directory: {GRAFANA_DATA_DIR}')

    #     if not os.path.isdir(GRAFANA_PROVISIONING_DIR):
    #         os.makedirs(GRAFANA_PROVISIONING_DIR, exist_ok=True)
    #         print(f'init(): Created Grafana provisioning directory: {GRAFANA_PROVISIONING_DIR}')

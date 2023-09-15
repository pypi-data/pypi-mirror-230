from .camera_app import camera_app
from .scenario_app import scenario_app
from .auth_app import auth_app
from .device_app import device_app
from .pipeline_app import pipeline_app
# from .web_app import web_app
from .models_app import models_app
from .commands import init_cmd, stop_cmd, status_cmd,update_visionai_images_cmd, register_company_cmd, register_cmd
from .start_stop_influx_db import influx_db
from .start_stop_model_server import models_server_app
from .start_stop_redis_grafana import  redis_grafana_app
from .start_stop_web_app import web_app


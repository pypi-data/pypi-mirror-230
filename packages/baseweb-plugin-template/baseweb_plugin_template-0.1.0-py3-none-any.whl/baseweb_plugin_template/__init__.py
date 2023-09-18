__version__ = "0.1.0"

import logging
logger = logging.getLogger(__name__)

import os

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
FORMAT    = "[%(name)s] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

# "silence" lower-level modules
for module in [ "gunicorn.error", "baseweb.socketio", "baseweb.web", "baseweb.interface" ]:
  module_logger = logging.getLogger(module)
  module_logger.setLevel(logging.WARN)
  if len(module_logger.handlers) > 0:
    module_logger.handlers[0].setFormatter(formatter)

from baseweb.interface import register_component, register_static_folder

HERE = os.path.dirname(__file__)

register_static_folder(os.path.join(HERE, "static"))

COMPONENTS = os.path.join(HERE, "components")
for component in [
  "page",
]:
  register_component(f"{component}.js", COMPONENTS)

# expose baseweb server and perform additional configuration
from baseweb.web import server

server.config["TEMPLATES_AUTO_RELOAD"] = True
server.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", default="local")

logger.info("✅ everything loaded...")

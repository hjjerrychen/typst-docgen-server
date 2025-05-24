import os
import sys


from fastapi import FastAPI
from docgen.docgen import DocGen
from config.config import Config
from service.service import DocGenService
import uvicorn

DEFAULT_CONFIG_PATHS = ["./config.toml", "/etc/secrets/config.toml"]

def main():
    config_path_env = os.getenv("CONFIG_PATH")
    config_path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    config = Config([config_path_env, config_path_arg] + DEFAULT_CONFIG_PATHS).get_config()

    docgen = DocGen(config.assets.templates_dir, config.assets.fonts_dir)
    server = FastAPI()
    service = DocGenService(server, docgen, config.server.api_key)

    service.start(config.server.host, config.server.port)


if __name__ == "__main__":
    main()

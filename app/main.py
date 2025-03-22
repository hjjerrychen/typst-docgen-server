from typing import Union

from fastapi import FastAPI
from docgen.docgen import DocGen
from config.config import Config
from service.service import DocGenService
import uvicorn


def main():
    config = Config("./config.toml").get_config()

    docgen = DocGen(config.assets.templates_dir, config.assets.fonts_dir)
    server = FastAPI()
    service = DocGenService(server, docgen)

    service.start(config.server.host, config.server.port)


if __name__ == "__main__":
    main()

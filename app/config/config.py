import toml
import os
from pydantic import BaseModel, EmailStr, PositiveInt, DirectoryPath


class ServerConfig(BaseModel):
    host: str
    port: PositiveInt
    api_key: str

class AssetsConfig(BaseModel):
    templates_dir: DirectoryPath
    fonts_dir: list[DirectoryPath]

class DocGenConfig(BaseModel):
    server: ServerConfig
    assets: AssetsConfig


class Config:
    def __init__(self, paths: list[str]):
        self.paths = paths
        self.config = self._load_config()

    def get_config(self) -> DocGenConfig:
        config = DocGenConfig.model_validate(self.config)
        config.assets.templates_dir = os.path.abspath(config.assets.templates_dir)
        config.assets.fonts_dir = [os.path.abspath(font_dir) for font_dir in config.assets.fonts_dir]
        return config

    def _load_config(self) -> dict:
        for path in self.paths:
            if path and os.path.exists(path):
                with open(path, "r") as f:
                    return toml.load(f)
        raise FileNotFoundError(f"Config file {self.paths} does not exist")
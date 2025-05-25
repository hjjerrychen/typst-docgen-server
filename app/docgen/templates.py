from dataclasses import dataclass
from enum import Enum
import semantic_version as semver
import os
import toml
import pprint


@dataclass(frozen=True)
class Template:
    ENTRYPOINT = "docgen.typ"
    TEMPLATE_CONFIG = "docgen.toml"
    name: str
    path: str
    versions_required_params: dict[str, list[str]]

    def get_path(self, version: str) -> str:
        return f"{self.path}/{version}/{Template.ENTRYPOINT}"

    def has_version(self, version: str):
        return version in self.versions_required_params.keys()

    def get_versions(self):
          return self.entrypoint.keys()

    def get_required_params(self, version: str):
        return self.versions_required_params.get(version, [])

class TemplateResolver:
    def __init__(self, path: str):
        self.path = path
    
    def resolve(self) -> dict[str, Template]:
      templates = {}
      directories = self._get_template_directories()
      for directory in directories:
        versions_required_params = self._get_versions_required_params(os.path.join(self.path, directory))
        if (len(versions_required_params) > 0):
          templates[directory] = Template(
                name=directory,
                path=os.path.join(self.path, directory),
                versions_required_params=versions_required_params,
            )
      print("Detected templates:", pprint.pformat(templates))
      return templates

    def _get_versions_required_params(self, dir: str) -> dict[str, list[str]]:
        versions_required_params: dict[str, list[str]] = {}
        for version in self._get_versions(dir):
            toml_path = os.path.join(self.path, dir, version, Template.TEMPLATE_CONFIG)
            if os.path.exists(toml_path):
                with open(toml_path, "r") as f:
                  versions_required_params[version] = toml.load(f)["parameters"]["required"]
        return versions_required_params

    def _get_versions(self, dir: str) -> list[str]:
        versions = os.listdir(os.path.join(self.path, dir))
        return [version for version in versions if TemplateResolver._is_valid_version(os.path.join(self.path, dir), version)]

    def _get_template_directories(self) -> list[str]:
        return [dir for dir in os.listdir(self.path) if TemplateResolver._is_valid_dir(os.path.join(self.path, dir), dir)]
    
    def _is_valid_version(full_path: str, version: str) -> bool:
        return TemplateResolver._is_valid_dir(full_path, version) and semver.validate(version)

    def _is_valid_dir(full_path: str, dir: str) -> bool:
        return os.path.isdir(full_path) and not dir.startswith("_") and not dir.startswith(".")

    def _get_enum_name(name: str) -> str:
        return ''.join(filter(str.isalnum, name)).upper()

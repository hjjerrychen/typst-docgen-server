import os
from docgen.templates import Template, TemplateResolver
from docgen.typst import Typst

class DocGen:
    def __init__(self, templates_dir: str, fonts_dir: list[str]):
        if not os.path.isdir(templates_dir):
            raise NotADirectoryError(f"Templates directory '{templates_dir}' does not exist.")
        for font_dir in fonts_dir:
          if not os.path.isdir(font_dir):
              raise NotADirectoryError(f"Fonts directory '{font_dir}' does not exist.")
              # template resolver needs to check more things 
        self.templates: dict[str, Template] = TemplateResolver(templates_dir).resolve()
        self.fonts_dir = fonts_dir

    def generate(self, template_id: str, version: str, data: dict):
      if not self.template_id_exists(template_id):
        raise ValueError(f"Template '{template_id}' does not exist.")
      if not self.version_exists(template_id, version):
        raise ValueError(f"Version '{version}' does not exist for template '{template_id}'.")

      extra_params = self.check_extra_params(template_id, version, data)
      if len(extra_params) > 0:
        raise TypeError(f"Extra parameters for version '{version}' of template '{template_id}' are provided: {', '.join(extra_params)}")

      missing_params = self.check_required_params(template_id, version, data)
      if len(missing_params) > 0:
        raise TypeError(f"Required parameters for version '{version}' of template '{template_id}' are missing: {', '.join(missing_params)}")

      return Typst.render(self.templates[template_id].get_path(version), self.fonts_dir, data)

    def template_id_exists(self, template_id: str):
        return template_id in self.templates

    def version_exists(self, template_id: str, version: str):
        return self.templates[template_id].has_version(version)

    def check_required_params(self, template_id: str, version: str, data: dict):
        return list(set(self.templates[template_id].get_required_params(version)).difference(data.keys()))

    def check_extra_params(self, template_id: str, version: str, data: dict):
        return list(set(data.keys()).difference(self.templates[template_id].get_required_params(version)))


import os
from docgen.templates import Template, TemplateResolver
from docgen.typst import Typst

class DocGen:
    def __init__(self, templates_dir: str, fonts_dir: list[str]):
        if not os.path.exists(templates_dir):
            raise ValueError(f"Templates directory '{templates_dir}' does not exist.")
        for font_dir in fonts_dir:
          if not os.path.exists(font_dir):
              raise ValueError(f"Fonts directory '{font_dir}' does not exist.")
              # template resolver needs to chgeck more things 
        self.templates: dict[str, Template] = TemplateResolver(templates_dir).resolve()
        self.fonts_dir = fonts_dir

    def generate(self, template_id: str, version: str, data: dict):
      if not self.template_id_exists(template_id):
        raise ValueError(f"Template '{template_id}' does not exist.")
      if not self.version_exists(template_id, version):
        raise ValueError(f"Version '{version}' does not exist for template '{template_id}'.")
      if not self.check_required_params(template_id, version, data):
        raise ValueError(f"Required parameters for version '{version}' of template '{template_id}' are missing.")

      return Typst.render(self.templates[template_id].get_path(version), self.fonts_dir, data)

    def template_id_exists(self, template_id: str):
        return template_id in self.templates

    def version_exists(self, template_id: str, version: str):
        return self.templates[template_id].has_version(version)

    def check_required_params(self, template_id: str, version: str, data: dict):
        return set(self.templates[template_id].get_required_params(version)).issubset(data.keys())



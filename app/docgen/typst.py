import typst
import os

class Typst:
    def render(typst_template_path: str, font_dirs: list[str], sys_inputs: dict):
        return typst.compile(typst_template_path, font_paths=font_dirs, sys_inputs=sys_inputs)

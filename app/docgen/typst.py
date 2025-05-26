import typst
import json

class Typst:
    
    @classmethod
    def render(cls, typst_template_path: str, font_dirs: list[str], data: dict) -> bytes:
        try:
            sys_inputs = {"data": json.dumps(data)}
            return typst.compile(typst_template_path, font_paths=font_dirs, sys_inputs=sys_inputs)
        except Exception as e:
            print(f"Failed to render template '{typst_template_path}': {str(e)}")
            raise Exception(f"Failed to render template '{typst_template_path}': {str(e)}")

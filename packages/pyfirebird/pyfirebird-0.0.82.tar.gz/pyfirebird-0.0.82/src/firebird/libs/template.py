from typing import Any
from pathlib import Path
import jinja2

JINJA_ENV   = jinja2.Environment()
BASE_DIR    = Path(__file__).resolve().parent.parent

def render_template(template_name:str, context:Any)->str:
    template_filename = BASE_DIR / f"resources/templates/{template_name}"

    with open(template_filename, "rt") as f:
        content = f.read()
        template = JINJA_ENV.from_string(content)
        return template.render(context)


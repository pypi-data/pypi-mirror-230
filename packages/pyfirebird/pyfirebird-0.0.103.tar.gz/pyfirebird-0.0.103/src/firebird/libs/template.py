from pathlib import Path
import jinja2

JINJA_ENV   = jinja2.Environment()
BASE_DIR    = Path(__file__).resolve().parent.parent

def render_template(template_name:str, context:dict={})->str:
    """Render Jinja template with context

    Args:
        template_name (str): Template name, template are are stored at directory resources/templates
        context (dict): A dict represent the rendering context

    Returns:
        str: Rendered template
    """
    template_filename = BASE_DIR / f"resources/templates/{template_name}"

    with open(template_filename, "rt") as f:
        content = f.read()
        template = JINJA_ENV.from_string(content)
        return template.render(context)


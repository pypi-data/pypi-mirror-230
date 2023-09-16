import os

from markupsafe import Markup
from starlette.templating import Jinja2Templates

from . import db as db, keymodel as bm, form as fm, element, functions, model

templates = Jinja2Templates(directory=os.path.join(os.getcwd(), 'templates'))
templates.env.globals['config'] = db.config
templates.env.globals['str'] = str
templates.env.globals['get_model'] = bm.get_model
templates.env.globals['Form'] = fm.Form
templates.env.globals['ffield'] = fm.BasicFormField
templates.env.globals['lang'] = db.config.get("HTML_LANG", default='en')
templates.env.globals['element'] = element.Element
templates.env.globals['Markup'] = Markup
templates.env.globals['today'] = functions.today
templates.env.globals['today_iso'] = lambda : functions.today().isoformat()
templates.env.globals['now_iso'] = functions.now_iso
templates.env.globals['random_id'] = functions.random_id


INDEX_TEMPLATE_STRING = """
<!doctype html>
<html lang="{{lang}}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{title}}</title>
    <script src="/static/js/anime.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
  </head>
  <body>
  {% block body %}
    <h1>Hello, world!</h1>
    <div style="width: 100px; height: 200px; background-color: red"></div>
  {% endblock %}
  <script src="/static/js/body.js"></script>
  </body>
</html>
"""

def from_string(string: str, **kwargs) -> str:
    return templates.env.from_string(string).render(**kwargs)


class Render:
    
    @staticmethod
    def list_group_item(instance: model.ModelType):
        return element.Li(class_names='list-group-item',children=str(instance))
    
    @staticmethod
    def list_group(instances: list[model.ModelType]):
        return element.Ul(class_names='list-group', children=[Render.list_group_item(item) for item in instances])
    
    @staticmethod
    def list_group_title(model: type[model.ModelType]):
        return element.H3(children=f'Lista de {model.plural()}', class_names='small-caps')
    
templates.env.globals['Render'] = Render
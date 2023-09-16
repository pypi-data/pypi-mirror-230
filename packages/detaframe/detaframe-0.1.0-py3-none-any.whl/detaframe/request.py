from collections import defaultdict

from starlette.requests import Request

from . import jinja

async def template_response(template: str, **kwargs):
    return jinja.templates.TemplateResponse(template, kwargs)


async def get(template_string: str, **kwargs):
    return jinja.templates.get_template()

async def process_form_data(request: Request):
    form_data = await request.form()
    print(form_data)
    result = defaultdict(list)
    cleaned = {**request.path_params}
    for k, v in form_data.multi_items():
        result[k].append(v)
    print(result)
    for k, v in result.items():
        if len(v) == 0:
            cleaned[k] = None
        elif len(v) == 1:
            cleaned[k] = v[0]
        else:
            cleaned[k] = v
    return cleaned
    
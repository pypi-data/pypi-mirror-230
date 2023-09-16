from __future__ import annotations

import io
from contextvars import ContextVar
from collections import ChainMap
from starlette.requests import Request
from starlette.responses import HTMLResponse

from detaframe import ctx as ct, keymodel as bm, functions as fn, jinja as tp
from detaframe.dev import orm as orm

PathPrefixVar = ContextVar('PathPrefixVar', default='')
ClassNameVar = ContextVar('ClassNameVar', default='')
TemplateStringVar = ContextVar('TemplateStringVar', default='')
TemplateDataVar = ContextVar('TemplateDataVar', default=dict())

def datalist_option(instance: bm.ModelType, data_fields: set[str] = None) -> str:
    data_fields = data_fields or instance.DATALIST_FIELDS or set()
    
    
    def data_field(name: str) -> str:
        
        def cleaned_name() -> str:
            return name.replace(".", "-")
        
        if val := fn.getter(instance, name):
            return f' data-{cleaned_name()}="{str(val)}" '
        return ''
    
    return f'<option id="{instance.classname()}.{instance.key}" value="{instance.key}" data-table="{instance.table()}"' \
           f'{fn.join([data_field(name) for name in data_fields or instance.datalist_fields()])}>{str(instance)}</option>'


def detail_link(instance: bm.ModelType) -> str:
    
    def url():
        if path:= ct.context.get(PathPrefixVar):
            return f'{path}/{instance.item_name()}/{instance.key}'
        return f'/{instance.item_name()}/{instance.key}'
    
    with io.StringIO() as fl:
        fl.write(f'<a href="{url()}"')
        if class_name:= ct.context.get(ClassNameVar):
            fl.write(f' class="{class_name}" ')
        fl.write(f'>{str(instance)}')
        fl.write('</a>')
        return fl.getvalue()


tp.templates.env.globals['datalist_option'] = datalist_option
tp.templates.env.globals['detail_link'] = detail_link


def request_data(request: Request):
    return {**ChainMap({**request.path_params}, {**request.query_params}, {**request.session})}


async def model_search_response(request: Request):
    file = """
<ul class="list-group ms-auto ">
	{% set item_name = model.item_name() %}
	{% for item in instances %}
		<li class="list-group-item bg-dark">
			<a href="/{{ item_name }}/{{ item.key }}" class="list-group-item-action text-white search-item">{{ str(item) }}</a>
		</li>
	{% endfor %}
</ul>

<style>
	.search-item:hover{
		color: black!important;
	}
</style>
    """
    search = request.query_params.get('search')
    model = bm.get_model(request)
    if search:
        instances = await orm.instances(model, {'search?contains': fn.normalize_lower(search)})
        return tp.templates.env.from_string(file).render({
                'request': request,
                'model': model,
                'instances': instances,
        })
    return HTMLResponse('nada encontrado')



async def model_list_group_responde(request: Request):
    file = """
    <div id="{{ model.item_name() }}__list">
        <h5 id="{{ model.item_name() }}__list__title" class="list-title">{{ model.plural() }}</h5>
        <ul class="list-group">
        {% for item in instances %}
            <li class="list-group-item">
              {{ detail_link(item) }}
            </li>
        {% endfor %}
        </ul>
    </div>
    """
    model = bm.get_model(request)
    ct.context.run(ClassNameVar.set, "list-group-item-action detail-link")
    instances = await orm.instances(model, {**request.query_params})
    return tp.templates.env.from_string(file).render(
            {
                    'request': request,
                    'instances': instances,
                    'model': model
            }
    )


async def model_datalist_options_response(request: Request):
    file = """
    {% for item in instances %}
        {{ datalist_option(item) }}
    {% endfor %}
    """
    model = bm.get_model(request)
    instances = await orm.instances(model, {**request.query_params})
    return tp.templates.env.from_string(file).render(
            {
                    'request': request,
                    'instances': instances,
                    'model': model
            }
    )


async def render_from_string(request: Request):
    return tp.templates.env.from_string(ct.context.get(TemplateStringVar)).render(request=request, **ct.context.get(TemplateDataVar))
# from starlette.requests import Request
#
# from . import orm, jinja, model, element
#
#
# def list_group_item(instance: model.ModelType, **kwargs) -> element.Element:
#     return element.Li(class_names='list-group-item', children=str(instance), htmx=dict(get=f'/htmx/detail/{instance.item_name()}/{instance.key}'))
#
#
# async def list_response_content(request: Request):
#     md = model.get_model(request)
#     instances = await orm.instances(md, {**request.query_params})
#     template_string = """
# <div id="{{ model.item_name() }}__list__container">
#     <h3 id="{{ model.item_name() }}__list__title">{{ model.plural() }}</h3>
#     <ul id="{{ model.item_name() }}__list" class="list-group">
#         {% for item in instances %}
#             {{ list_group_item(item) }}
#         {% endfor %}
#     </ul>
# </div>
#     """
#     return jinja.from_string(template_string, request=request, model=md, instances=instances, list_group_item=list_group_item)
#
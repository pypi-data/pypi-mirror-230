from __future__ import annotations

import secrets

from starlette.requests import Request

from . import element as el, model



def icon(name: str) -> str:
    return f'<i class="bi {name}"></i>'

def list_group_item(instance: model.ModelType, **kwargs) -> el.Element:
    return el.Li(class_names='list-group-item', children=str(instance), **kwargs)

    
def delete_button(instance: model.Model, initial_path: str = '/delete'):
    return el.Element('button', class_names='btn-trash', htmx={
            'confirm': f"Confirma excluir {instance.singular().lower()}, chave {instance.key}. Esta ação não pode ser desfeita.",
            'post': f'{initial_path}/{instance.item_name()}/{instance.key}'
    }, children='<i class="bi bi-trash3"></i>')


def detail_page_link(instance: model.Model, initial_path: str = '/detail', **kwargs):
    return el.A(href=f'{initial_path}/{instance.item_name()}/{instance.key}', children=str(instance), **kwargs)

def detail_htmx_link(instance: model.Model, initial_path: str = '/htmx/detail', trigger: str = 'click'):
    id = f'{instance.item_name()}-{instance.key}'
    base_cls_name = 'detail-htmx'
    htmx = dict(get=f'{initial_path}/{instance.item_name()}/{instance.key}', target=f'#{id}__display', trigger=trigger)
    return el.Div(id=f'{id}__container', class_names=f'{base_cls_name}__container', children=[
            el.Div(children=str(instance), htmx=htmx, class_names=f'{base_cls_name}__link', id=f'{id}__link'),
            el.Div(id=f'{id}__display', class_names=f'{base_cls_name}__display')
    ])


def datalist(path: str):
    return el.DataList(htmx=dict(get=path, trigger='load'))
    
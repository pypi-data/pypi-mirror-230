from __future__ import annotations

from contextvars import copy_context, ContextVar
from functools import cache
from typing import Any, Optional, overload

from anyio import create_task_group

from . import keymodel as bm


context = ctx = copy_context()


async def set_ctxvar_value(model: type[bm.KeyModelType], lazy: bool = False):
    if lazy:
        if not get_ctxvar_value(model):
            context.run(model.CTXVAR.set, {i.get('key'): i for i in await model.fetch_all(query=model.FETCH_QUERY)})
    else:
        context.run(model.CTXVAR.set, {i.get('key'): i for i in await model.fetch_all(query=model.FETCH_QUERY)})


def get_ctxvar_value(model: type[bm.KeyModelType]):
    return context.get(model.CTXVAR)


async def populate_context(dependants: list[type[bm.KeyModelType]], lazy: bool = False):
    async with create_task_group() as tks:
        for item in dependants:
            tks.start_soon(set_ctxvar_value, item, lazy)
    
            
def data_from_context(model: type[bm.KeyModelType], key: str) -> Optional[dict]:
    try:
        return get_ctxvar_value(model)[key]
    except KeyError:
        return None


def instance_from_context(model: type[bm.KeyModelType] | str, key: str) -> Optional[bm.KeyModelType]:
    if isinstance(model, str):
        model = bm.get_model(model)
    data = data_from_context(model, key)
    if data:
        return model(**data)
    return None
    






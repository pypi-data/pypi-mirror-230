# from __future__ import annotations
#
# import json
# from functools import cache
# from typing import Optional
#
# from anyio import create_task_group
#
#
# from . import keymodel as km, functions as fn, db, ctx
#
#
# async def update_model_context(model: type[km.KeyModelType], lazy: bool = False):
#     await ctx.populate_context(dependant_models(model), lazy=lazy)
#
#
# async def instances(model: type[km.KeyModelType], query: list[dict] | dict | None = None, lazy: bool = False) -> list[km.KeyModelType]:
#     await update_model_context(model, lazy=lazy)
#     data = await model.fetch_all(query or model.FETCH_QUERY)
#     return [model(**i) for i in data]
#
#
# async def model_instance(model: type[km.KeyModel], key: str) -> Optional[km.KeyModelType]:
#     await update_model_context(model)
#     data = await model.fetch_one(key)
#     if data:
#         return model(**data)
#     return None
#
#
# @cache
# def direct_dependant_models(model: type[km.ModelType]):
#     result = list()
#     for key_name in direct_dependant_fields(model):
#         try:
#             result.append(km.ModelMap[key_name.replace('_key', '')])
#         except KeyError:
#             if key_name == 'provider_key':
#                 result.extend([km.get_model('doctor'), km.get_model('therapist')])
#             elif key_name == 'profile_key':
#                 result.extend([km.get_model('doctor'), km.get_model('therapist'),
#                                km.get_model('employee'), km.get_model('patient')])
#             elif key_name == 'staff_key':
#                 result.extend([km.get_model('doctor'), km.get_model('therapist'),
#                                km.get_model('employee')])
#     return fn.filter_uniques(result)
#
#
# @cache
# def direct_dependant_fields(model: type[km.ModelType]):
#     return [k for k, v in model.model_fields.items() if v.annotation in [Optional[model.Key], model.Key]]
#
#
# @cache
# def dependant_models(model: type[km.ModelType]):
#     result = list()
#
#     def recursive(_model: type[km.ModelType]):
#         result.append(_model)
#         if sub:= direct_dependant_models(_model):
#             for item in sub:
#                 recursive(item)
#
#     for md in direct_dependant_models(model):
#         recursive(md)
#
#     return fn.filter_uniques(result)
#
#
# def asjson(instance: km.ModelType, **kwargs):
#     return json.loads(instance.model_dump_json(**kwargs))
#
# async def save(instance: km.ModelType, **kwargs):
#     saved = await db.save(instance.table(), asjson(instance, **kwargs))
#     if saved:
#         return type(instance)(**saved)
#     return None
#
# async def save_new(instance: km.ModelType, **kwargs):
#     exist = await instance.exist()
#     if not exist:
#         return await save(instance, **kwargs)
#     return None
#
#

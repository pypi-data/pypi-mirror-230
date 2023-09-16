from __future__ import annotations

from collections import ChainMap
from contextvars import ContextVar, copy_context
from functools import cache, wraps
from typing import Any, Optional, overload, TypeVar

from typing_extensions import Self

from . import keymodel, db, element, ctx


ModelMap: ChainMap[str, ModelType] = keymodel.ModelMap


class Model(keymodel.KeyModel):
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        for key_name in self.reference_keys():
            key = getattr(self, key_name)
            if '.' in key:
                model_name, key_value = key.split('.')
                model = keymodel.get_model(model_name)
                setattr(self, model.item_name(), ctx.instance_from_context(model, key_value))
            else:
                item_name = key_name.replace('_key', '')
                setattr(self, item_name, ctx.instance_from_context(item_name, key))
    
    @classmethod
    async def initiate(cls, *args, **kwargs) -> Self:
        result = None
        try:
            result = cls(*args, **kwargs)
        except:
            await cls.update_context()
            result = cls(*args, **kwargs)
        finally:
            return result
        
    @classmethod
    async def update_context(cls, lazy: bool = False):
        await ctx.populate_context(cls.dependants(), lazy=lazy)
        
    @classmethod
    async def instance_list(cls, query: list[dict] | dict | None = None, lazy: bool = False):
        await cls.update_context(lazy=lazy)
        return [cls(**i) for i in await cls.fetch_all(query)]
    
    @classmethod
    async def sorted_instance_list(cls, query: list[dict] | dict | None = None, lazy: bool = False):
        return sorted(await cls.instance_list(query=query, lazy=lazy))
    
    @classmethod
    async def instanciate(cls, key: str) -> Self:
        result = None
        data = await cls.fetch_one(key)
        try:
            result = cls(**data)
        except:
            await cls.update_context(lazy=True)
            result = cls(**data)
        finally:
            return result
        
        
    async def save_new(self, **kwargs):
        if exist:= await self.exist():
            return await self.initiate(**exist)
        else:
            saved = await self.PROJECT.save(self.table(), self.asjson(**kwargs))
            if saved:
                return await self.initiate(**saved)
            return None
            
            
    async def update(self, **kwargs):
        if self.key:
            saved = await self.PROJECT.save(self.table(), self.asjson(**kwargs))
            if saved:
                return await self.initiate(**saved)
            return None
        raise Exception('Apenas instâncias com "key" pode ser atualizadas.')
        
        
    def html_option(self, value: str = None, inner_text: str = None, **kwargs):
        return element.Element('option', value=value or self.key, children=inner_text or str(self), **kwargs)
    
    def key_with_str(self):
        return f'{self.key} | {self}'
    

    
ModelType = TypeVar('ModelType', bound=Model)


def model_map(cls: type[Model]):
    @wraps(cls)
    def wrapper():
        assert cls.EXIST_QUERY, 'cadastrar "EXIST_QUERY" na classe "{}"'.format(cls.__name__)
        keymodel.ModelMap[cls.item_name()] = cls
        cls.CTXVAR = ContextVar(f'{cls.__name__}Var', default=dict())
        cls.PROJECT = db.DetaProject(cls.PROJECT_KEY_NAME)
        return cls
    return wrapper()


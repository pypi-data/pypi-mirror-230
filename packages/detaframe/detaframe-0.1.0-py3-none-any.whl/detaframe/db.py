from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Callable, Literal, Optional

from anyio import create_task_group
from deta import Deta
from deta.base import FetchResponse
from starlette.config import Config

from . import functions

TABLE: str
KEY: str | None
DATA: dict | list | str | int | float | bool
EXPIRE_IN: int | None
EXPIRE_AT: int | float | datetime.datetime | None


config = Config(env_file='.env')

project = Deta(project_key=config.get('DATA_KEY', default=config.get("DETA_PROJECT_KEY")))


class DatabaseException(BaseException):
    ...



async def fetch_all(table: str, query: dict | list[dict] | None) -> list[Optional[dict]]:
    base = project.AsyncBase(table)
    try:
        result = await base.fetch(query=query)
        data = result.items
        while result.last:
            result = await base.fetch(query=query, last=result.last)
            data.extend(result.items)
        return data
    finally:
        await base.close()
    
    
async def fetch_one(table: str, key: str) -> Optional[dict]:
    base = project.AsyncBase(table)
    try:
        return await base.get(key)
    finally:
        await base.close()
        

async def fetch(table: str, query: dict | list[dict] | None = None, last: str | None = None) -> FetchResponse:
    base = project.AsyncBase(table)
    try:
        return await base.fetch(query=query, last=last)
    finally:
        await base.close()

async def create_key(table: str, key: str = None) -> str:
    base = project.AsyncBase(table)
    try:
        result = await base.insert(data=dict(), key=key)
        if result:
            return result.get('key')
    finally:
        await base.close()
    

async def save(table: str, data: dict):
    base = project.AsyncBase(table)
    key = data.pop('key', None)
    try:
        return await base.put(data=data, key=key)
    finally:
        await base.close()
        
        
async def exist(table: str, query: dict[str, str] | list[dict[str, str]]):
    result = await fetch(table, query=query)
    if result.count == 1:
        return result.items[0]
    elif result.count == 0:
        return None
    else:
        raise DatabaseException('a pesquisa "exist" retornou mais de uma possibilidade')
        
        
async def delete(table: str, key: str):
    base = project.AsyncBase(table)
    try:
        await base.delete(key)
    finally:
        await base.close()
        
        
class DetaProject:
    def __init__(self, key_name: str = None, project_key: str = None, mode: Literal['r', 'w'] = 'r'):
        assert key_name or project_key
        self.key_name = key_name or 'DETA_PROJECT_KEY'
        self.project_key = project_key or config.get(self.key_name)
        self.mode = mode
        self.deta = Deta(self.project_key)

    
    async def fetch_all(self, table: str, query: dict | list[dict] | None) -> list[Optional[dict]]:
        base = self.deta.AsyncBase(table)
        try:
            result = await base.fetch(query=query)
            data = result.items
            while result.last:
                result = await base.fetch(query=query, last=result.last)
                data.extend(result.items)
            return data
        finally:
            await base.close()
    
    async def fetch_one(self, table: str, key: str) -> Optional[dict]:
        base = self.deta.AsyncBase(table)
        try:
            return await base.get(key)
        finally:
            await base.close()
    
    async def fetch(self, table: str, query: dict | list[dict] | None = None, last: str | None = None) -> FetchResponse:
        base = self.deta.AsyncBase(table)
        try:
            return await base.fetch(query=query, last=last)
        finally:
            await base.close()
    
    async def create_key(self, table: str, key: str = None) -> str:
        base = self.deta.AsyncBase(table)
        try:
            result = await base.insert(data=dict(), key=key)
            if result:
                return result.get('key')
        finally:
            await base.close()
    
    async def save(self, table: str, data: dict):
        base = self.deta.AsyncBase(table)
        key = data.pop('key', None)
        try:
            return await base.put(data=data, key=key)
        finally:
            await base.close()
    
    async def exist(self, table: str, query: dict[str, str] | list[dict[str, str]]):
        result = await self.fetch(table, query=query)
        if result.count == 1:
            return result.items[0]
        elif result.count == 0:
            return None
        else:
            raise DatabaseException('a pesquisa "exist" retornou mais de uma possibilidade')
    
    async def delete(self, table: str, key: str):
        base = self.deta.AsyncBase(table)
        try:
            await base.delete(key)
        finally:
            await base.close()
            
    async def put(self, table: TABLE, data: DATA, key: KEY = None, *, expire_in: EXPIRE_IN = None, expire_at: EXPIRE_AT = None) -> dict:
        base = self.deta.AsyncBase(table)
        _key = key or data.pop('key', None)
        try:
            return await base.put(data, _key, expire_in=expire_in, expire_at=expire_at)
        finally:
            await base.close()
            
            
    async def insert(self, table: TABLE, data: DATA, key: KEY = None, *, expire_in: EXPIRE_IN = None, expire_at: EXPIRE_AT = None) -> dict:
        """
        Inserts a single item, but is different from put in that it will throw an error of the key already exists in the Base.
        :return: Returns a dict with the item’s data. If key already exists, raises an Exception. If key is not a non-empty string, raises a ValueError. If the operation did not complete successfully, raises an Exception.
        """
        base = self.deta.AsyncBase(table)
        _key = key or data.pop('key', None)
        try:
            return await base.insert(data, _key, expire_in=expire_in, expire_at=expire_at)
        finally:
            await base.close()
            
            
    async def put_many(self, table: TABLE, items: list[DATA], *, expire_in: EXPIRE_IN = None, expire_at: EXPIRE_AT = None) -> dict[str, list]:
        """
        Puts up to 25 items at once with a single call.
        :param table:
        :param items:
        :param expire_in:
        :param expire_at:
        :return: Returns a dict with "processed" and "failed" keys containing processed and failed items.
        """
        base = self.deta.AsyncBase(table)
        try:
            return await base.put_many(items, expire_in=expire_in, expire_at=expire_at)
        finally:
            await base.close()
            
    async def put_all(self, table: TABLE, items: list[DATA], *, expire_in: EXPIRE_IN = None, expire_at: EXPIRE_AT = None) -> dict[str, list]:
        """
        Puts all items at once.
        :param table:
        :param items:
        :param expire_in:
        :param expire_at:
        :return: Returns a dict with "processed" and "failed" keys containing processed and failed items.
        """
        base = self.deta.AsyncBase(table)
        patch = functions.paginate(items)
        processed, failed = list(), list()
        result = {'processed': list(), 'failed': list()}
        try:
            for g in patch:
                data = await base.put_many(g, expire_in=expire_in, expire_at=expire_at)
                processed.extend(data.get('processed', []))
                failed.extend(data.get('failed', []))
            return result
        finally:
            await base.close()
            
    async def update(self, table: str, updates: dict, key: str, *, expire_in: EXPIRE_IN = None, expire_at: EXPIRE_AT = None):
        base = self.deta.AsyncBase(table)
        try:
            await base.update(updates, key, expire_in=expire_in, expire_at=expire_at)
        finally:
            await base.close()
            
    
    async def migrate(self, origin: TABLE, destination: TABLE, key: KEY = None, parser: Callable = lambda x: x, query: dict|list[dict]|None = None):
        if key:
            return await self.put(destination, data=parser(await self.fetch_one(origin, key)))
        else:
            data = await self.fetch_all(origin, query=query)
            patchs = functions.paginate(data)
            for p in patchs:
                await self.put_many(destination, [parser(i) for i in p])
        return

        
            
    async def delete_fields(self, table: TABLE, fields: list[str], key: str = None, query: dict | list[dict] | None = None) -> Optional[dict[str, list[DATA]]]:
        base = self.deta.AsyncBase(table)
        updates = {k: base.util.trim() for k in fields}
        
        def apply(item: dict) -> dict:
            item.update(updates)
            return item
        
        async def process(k):
                await base.update(updates, k)
        try:
            if key:
                return await process(key)
            else:
                data = (apply(i) for i in await self.fetch_all(table, query=query))
                return await self.put_all(table, list(data))
                
        finally:
            await base.close()
            
            
            
class QueryComposer:
    
    @staticmethod
    def lt(key: str, value: int | float):
        return {f'{key}?lt': value}
    
    @staticmethod
    def lte(key: str, value: int | float):
        return {f'{key}?lte': value}


    @staticmethod
    def gte(key: str, value: int | float):
        return {f'{key}?gte': value}
    
    @staticmethod
    def ge(key: str, value: int | float):
        return {f'{key}?ge': value}
    
    @staticmethod
    def prefix(key: str, value: str):
        return {f'{key}?pfx': value}
    
    @staticmethod
    def range(key: str, value: list[int | float, int | float]):
        return {f'{key}?r': value}
    
    @staticmethod
    def contains(key: str, value: str):
        return {f'{key}?contains': value}
    
    @staticmethod
    def not_contains(key: str, value: str):
        return {f'{key}?not_contains': value}
    

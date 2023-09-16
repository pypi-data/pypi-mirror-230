from __future__ import annotations

import os.path
import re
from collections import defaultdict
from typing import ClassVar
from starlette.templating import Jinja2Templates
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.responses import HTMLResponse
from starlette.config import Config
from starlette.staticfiles import StaticFiles
from . import ctx, keymodel, form, middleware, model
from .dev import helper


class App(Starlette):
    ACTIONS: ClassVar[tuple[str]] = ('create', 'update', 'list', 'search', 'detail')
    def __init__(self, *args, **kwargs):
        routes = kwargs.pop('routes', [])

        if templates:= kwargs.pop('templates', None):
            self.templates = Jinja2Templates(directory=os.path.join(os.getcwd(), templates))
        else: self.templates = None
        if env:= kwargs.pop('env', None):
            self.config = Config(os.path.join(os.getcwd(), env))
        else: self.config = Config()
        self.auto = kwargs.pop('auto', True)
        if static:= kwargs.pop('static', None):
            self.static = StaticFiles(directory=os.path.join(os.getcwd(), static))
        else:
            self.static = None
        self.context = ctx.context
        
        if self.static:
            routes.append(self.static_mount())
        if self.auto:
            routes.append(self.auto_mount())
            
        kwargs['routes'] = routes
        middle = kwargs.pop('middleware', [])
        middle.extend(middleware.middleware)
        kwargs['routes'] = routes
        kwargs['middleware'] = middle
        super().__init__(*args, **kwargs)
        
    def extend_routes(self, routes: list[Route | Mount]):
        self.routes.extend(routes)
    
    @property
    def model_pattern(self):
        return re.compile(r'({})'.format('|'.join(keymodel.ModelMap.keys())))
    
    @property
    def action_pattern(self):
        return re.compile(r'({})'.format('|'.join(self.ACTIONS)))
        
    @staticmethod
    def route_methods(action: str):
        return {
                'update': ['GET', 'POST'],
                'create': ['GET', 'POST'],
            
        }.get(action, ['GET'])
    
    @staticmethod
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
        
    
    async def create_endpoint(self, request: Request):
        if result := self.model_pattern.search(request.url.path):
            md: model.ModelType = keymodel.ModelMap[result.group(0)]
            if request.method == 'POST':
                data = await self.process_form_data(request)
                await md.update_context()
                new = md(**data)
                return HTMLResponse(str(new))
    
            elif request.method == 'GET':
                return HTMLResponse(str(form.Form(md, request, action=f'/auto/create/{md.item_name()}')))
        return HTMLResponse(request.url.path)
        
    def create_mount(self):
        return Mount('/create', name='create', routes=[
                Route(f'/{item.item_name()}', self.create_endpoint, name=item.item_name(), methods=['GET', 'POST']) for item in keymodel.ModelMap.values()
        ])
    
    def static_mount(self):
        return Mount('/static', name='static', app=self.static)
    
    def auto_mount(self):
        return Mount('/auto', name='auto', routes=[
                self.create_mount()
        ])
        
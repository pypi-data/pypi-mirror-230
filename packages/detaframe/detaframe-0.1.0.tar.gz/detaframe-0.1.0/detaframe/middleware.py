import secrets

from starlette.requests import Request
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import Scope
from starlette_csrf import CSRFMiddleware

from . import db as db

csrf_secret = db.config.get('CSRF_SECRET', default=secrets.token_hex())

class ASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive, send):
        if scope["type"] == "http":
            scope['headers'].append((b'x-csrftoken', csrf_secret.encode('utf-8')))
            # request = Request(scope)
            #
            # if request.session:
            #     if request.session.get('user', None):
            #         if token:= request.cookies.get('csrftoken'):
            #             scope['headers'].append((b'x-csrftoken', token.encode('utf-8')))
        await self.app(scope, receive, send)
        
        
class LoginMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope)
            if not '/static' in request.url.path:
                if not '/login' in request.url.path:
                    if not request.session.get('user'):
                        scope['path'] = '/login'
        await self.app(scope, receive, send)
        

session_secret = db.config.get('SESSION_SECRET', default=secrets.token_hex())

middleware: list[Middleware] = [
        Middleware(SessionMiddleware, secret_key=session_secret),
        Middleware(ASGIMiddleware),
        # Middleware(CSRFMiddleware, secret=csrf_secret),
        # Middleware(LoginMiddleware),
]
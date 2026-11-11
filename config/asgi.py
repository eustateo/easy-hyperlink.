"""Serve Django and FastAPI together, optionally beneath a website path."""

import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Mount

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_app = get_asgi_application()

from django.conf import settings  # noqa: E402
from api import app as api_app  # noqa: E402
from config.middleware import PublicAppMiddleware  # noqa: E402

routes = [Mount('/api', app=api_app), Mount('/', app=django_app)]
site = Starlette(routes=routes)
if settings.APP_BASE_PATH:
    site = Starlette(routes=[Mount(settings.APP_BASE_PATH, app=site)])

middleware = [Middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)]
if not settings.DEBUG:
    middleware.append(Middleware(HTTPSRedirectMiddleware))

application = PublicAppMiddleware(
    Starlette(routes=[Mount('/', app=site)], middleware=middleware),
    trust_cloudflare=os.environ.get('TRUST_CLOUDFLARE', 'false').lower() == 'true',
    production=not settings.DEBUG,
)

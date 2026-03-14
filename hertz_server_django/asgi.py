"""
ASGI config for hertz_server_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hertz_server_django.settings')

# Import Django first to ensure proper initialization
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import other modules AFTER Django setup
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Import websocket routing AFTER Django setup to avoid AppRegistryNotReady
from hertz_demo import routing as demo_routing

if 'hertz_studio_django_yolo' in settings.INSTALLED_APPS:
    from hertz_studio_django_yolo import routing as yolo_routing
    websocket_urlpatterns = (
        demo_routing.websocket_urlpatterns +
        yolo_routing.websocket_urlpatterns
    )
else:
    websocket_urlpatterns = demo_routing.websocket_urlpatterns

# 在开发环境下放宽Origin校验，便于第三方客户端（如 Apifox、wscat）调试
websocket_app = AuthMiddlewareStack(
    URLRouter(
        websocket_urlpatterns
    )
)

if getattr(settings, 'DEBUG', False):
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": websocket_app,
    })
else:
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(websocket_app),
    })


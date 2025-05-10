import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# from messenger.routing import application as ws_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messenger.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # "websocket": AuthMiddlewareStack(URLRouter(ws_application)),
    }
)

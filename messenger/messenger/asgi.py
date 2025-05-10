# messenger/asgi.py

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messenger.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
import chats.routing
from chats.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(URLRouter(chats.routing.websocket_urlpatterns)),
    }
)

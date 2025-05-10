from django.urls import re_path
from . import consumers
from chats.middleware import JWTAuthMiddleware

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<chat_id>\d+)/$",
        JWTAuthMiddleware(consumers.ChatConsumer.as_asgi()),
    ),
]

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from django.db import close_old_connections
import jwt
from django.conf import settings

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    try:
        validated_token = UntypedToken(token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return User.objects.get(id=user_id)
    except (TokenError, InvalidToken, jwt.DecodeError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        if token:
            token = token[0]
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

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
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    try:
        logger.info(f"Validating token: {token}")  # لاگ‌گذاری توکن دریافت شده
        validated_token = UntypedToken(token)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        logger.info(f"User ID from token: {user_id}")
        return User.objects.get(id=user_id)
    except (TokenError, InvalidToken, jwt.DecodeError, User.DoesNotExist) as e:
        logger.error(f"Token validation error: {e}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        if token:
            token = token[0]
            logger.info(f"Token received in WebSocket: {token}")
            try:
                # اعتبارسنجی مستقیم با jwt.decode
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                logger.info(f"User ID from token: {user_id}")
                user = await get_user_from_token(user_id)
                scope["user"] = user
            except jwt.ExpiredSignatureError:
                logger.error("Token has expired.")
                scope["user"] = AnonymousUser()
            except jwt.DecodeError:
                logger.error("Token decoding error.")
                scope["user"] = AnonymousUser()
            except Exception as e:
                logger.error(f"Error during token validation: {e}")
                scope["user"] = AnonymousUser()
        else:
            logger.warning("No token provided in WebSocket request.")
            scope["user"] = AnonymousUser()

        # لاگ‌گذاری وضعیت کاربر پس از احراز هویت
        logger.info(f"User after token validation: {scope['user']}")
        return await super().__call__(scope, receive, send)

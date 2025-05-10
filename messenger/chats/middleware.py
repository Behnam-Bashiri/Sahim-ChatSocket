import jwt
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from accounts.models import UserProfile

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token")
        if token:
            try:
                access_token = AccessToken(token[0])
                user_id = access_token["user_id"]
                user = await self.get_user(user_id)
                scope["user"] = user
            except Exception as e:
                scope["user"] = None
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            return await UserProfile.objects.aget(id=user_id)
        except UserProfile.DoesNotExist:
            return None

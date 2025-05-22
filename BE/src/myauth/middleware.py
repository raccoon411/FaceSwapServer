from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes a token from the query string and authenticates the user.
    """

    async def __call__(self, scope, receive, send):
        # Log connection attempt
        logger.debug(f"WebSocket connection attempt: {scope}")
        # Get the token from the query string
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(x.split('=') for x in query_string.split('&') if x)
        token = query_params.get('token', None)
        print(f"Token: {token}")
        # Set the user to AnonymousUser by default
        scope['user'] = AnonymousUser()

        # If token exists, try to authenticate
        if token:
            try:
                # Decode the token
                decoded_token = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                    options={"verify_signature": True}
                )
                user_id = decoded_token.get('user_id')
                if user_id:
                    scope['user'] = await get_user(user_id)
            except (InvalidToken, TokenError, jwt.PyJWTError):
                pass

        return await super().__call__(scope, receive, send)

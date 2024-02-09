from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

User = get_user_model()

@database_sync_to_async
def get_user_with_cookie(token_key):
    """
    Retrieve the user associated with the given token from cookies.
    """
    authentication = ()
    user, _ = authentication.authenticate_credentials(token_key)
    return user or AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware for WebSocket authentication using tokens stored in cookies.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Extract token from cookies
        headers = dict(scope['headers'])
        if b'cookie' in headers:
            cookies = headers[b'cookie'].decode()
            token_name = settings.AUTH_COOKIE
            token = parse_cookie(cookies).get(token_name)

            if token:
                user = await get_user_with_cookie(token)
                # Check if the user is an instance of the actual user model
                if isinstance(user, User):
                    scope['user'] = user
                else:
                    scope['user'] = AnonymousUser()
            else:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)

def parse_cookie(header):
    """
    Parse a cookie header to extract token.
    """
    cookies = {}
    for cookie in header.split(";"):
        parts = cookie.split("=", 1)
        if len(parts) == 2:
            cookies[parts[0].strip()] = parts[1].strip()
    return cookies

# Define a function to easily add this middleware
def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)

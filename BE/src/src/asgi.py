import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Set the Django settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# Initialize Django
django.setup()

# Import after Django setup to avoid the ImproperlyConfigured error
from faceswap import routing
from myauth.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": 
        JWTAuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
            )
    ),
})


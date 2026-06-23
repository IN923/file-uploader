"""
ASGI config for filesystem project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

# asgi.py

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import file_upload.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "filesystem.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        file_upload.routing.websocket_urlpatterns
    ),
})
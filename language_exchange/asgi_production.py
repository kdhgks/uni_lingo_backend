"""
프로덕션용 ASGI 설정 (WebSocket 지원)
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "language_exchange.settings_production")

# Django ASGI application을 먼저 초기화
django_asgi_app = get_asgi_application()

# 이제 Django가 설정된 후에 chat.routing을 import
import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})


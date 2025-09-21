"""
프로덕션용 WSGI 설정
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_exchange.settings_production')

application = get_wsgi_application()


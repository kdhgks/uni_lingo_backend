from django.urls import path
from . import views

urlpatterns = [
    path('healthz/', views.health_check, name='health_check'),
    path('health/db/', views.db_health_check, name='db_health'),
    path('health/redis/', views.redis_health_check, name='redis_health'),
    path('health/full/', views.full_health_check, name='full_health'),
]



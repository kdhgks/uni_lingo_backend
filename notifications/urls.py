from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.get_user_notifications, name='get_user_notifications'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
]



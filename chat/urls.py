from django.urls import path
from . import views

urlpatterns = [
    path('chat/rooms/', views.get_chat_rooms, name='get_chat_rooms'),
    path('chat/rooms/<int:room_id>/partner/', views.get_chat_room_partner, name='get_chat_room_partner'),
    path('chat/rooms/<int:room_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('chat/rooms/<int:room_id>/messages/send/', views.send_message, name='send_message'),
    path('chat/rooms/<int:room_id>/messages/read/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('chat/rooms/<int:room_id>/heart-reactions/', views.get_heart_reactions, name='get_heart_reactions'),
    path('chat/rooms/<int:room_id>/report/', views.report_user, name='report_user'),
    path('chat/rooms/<int:room_id>/leave/', views.leave_chat_room, name='leave_chat_room'),
    path('admin/reports/', views.get_reports, name='get_reports'),
]

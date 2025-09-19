from django.urls import path
from . import views

urlpatterns = [
    path('matching/partners/', views.get_partners, name='get_partners'),
    path('matching/request/', views.request_matching, name='request_matching'),
    path('matching/status/', views.get_matching_status, name='get_matching_status'),
    path('matching/simulate/', views.simulate_matching, name='simulate_matching'),
    # 관리자용 API
    path('matching/requests/', views.get_all_matching_requests, name='get_all_matching_requests'),
    path('matching/available-partners/', views.get_available_partners, name='get_available_partners'),
    path('matching/requests/<int:request_id>/approve/', views.approve_matching_request, name='approve_matching_request'),
    path('matching/requests/<int:request_id>/reject/', views.reject_matching_request, name='reject_matching_request'),
    path('matching/requests/<int:request_id>/matched-partner/', views.get_matched_partner, name='get_matched_partner'),
]

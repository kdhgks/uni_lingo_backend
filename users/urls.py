from django.urls import path
from . import views

urlpatterns = [
    # 인증 관련
    path('auth/login/', views.login, name='login'),
    path('auth/signup/', views.signup, name='signup'),
    
    # 사용자 관련
    path('users/profile/', views.ProfileView.as_view(), name='profile'),
    path('users/profile/<int:user_id>/', views.get_user_profile, name='get_user_profile'),
    path('users/change-password/', views.change_password, name='change_password'),
    path('users/delete/', views.delete_account, name='delete_account'),
]

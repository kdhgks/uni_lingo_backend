from django.contrib import admin
from .models import User, UserLanguage, UserInterest

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nickname', 'phone', 'gender', 'school', 'department', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('gender', 'university', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'nickname', 'phone', 'school', 'department')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'password')  # 비밀번호는 읽기 전용으로 설정
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('email', 'nickname', 'phone', 'gender', 'birth_date', 'profile_image')
        }),
        ('학생 정보', {
            'fields': ('student_name', 'school', 'department', 'student_id', 'university', 'student_card')
        }),
        ('권한', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('중요한 날짜', {
            'fields': ('last_login', 'date_joined')
        }),
        ('보안 정보', {
            'fields': ('password',),
            'description': '비밀번호는 해시화되어 저장되며 원본을 볼 수 없습니다.'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """비밀번호 필드는 항상 읽기 전용으로 설정"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # 기존 객체를 편집하는 경우
            readonly_fields.append('password')
        return readonly_fields

@admin.register(UserLanguage)
class UserLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'language', 'language_type')
    list_filter = ('language_type', 'language')
    search_fields = ('user__nickname', 'user__email', 'language')

@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'interest')
    list_filter = ('interest',)
    search_fields = ('user__nickname', 'user__email', 'interest')

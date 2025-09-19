from django.contrib import admin
from .models import MatchingRequest, MatchingPreference

# Register your models here.

@admin.register(MatchingRequest)
class MatchingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'gender_preference', 'university_preference', 'status', 'matched_partner', 'created_at')
    list_filter = ('status', 'gender_preference', 'university_preference', 'created_at')
    search_fields = ('user__nickname', 'user__email', 'matched_partner__nickname')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MatchingPreference)
class MatchingPreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'matching_request', 'teaching_languages', 'learning_languages', 'interests')
    search_fields = ('matching_request__user__nickname', 'matching_request__user__email')
    readonly_fields = ('teaching_languages', 'learning_languages', 'interests')

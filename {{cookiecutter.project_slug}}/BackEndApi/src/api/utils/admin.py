"""Admin configuration for LLM logging."""

from django.contrib import admin
from api.story.models import LLMLog


@admin.register(LLMLog)
class LLMLogAdmin(admin.ModelAdmin):
    """Admin interface for LLM logs."""

    list_display = (
        'request_id',
        'model',
        'status',
        'user',
        'response_model_name',
        'total_tokens',
        'duration_ms',
        'created',
    )

    list_filter = (
        'status',
        'model',
        'created',
    )

    search_fields = (
        'request_id',
        'user__email',
        'user__username',
        'response_model_name',
        'system_prompt',
        'user_input',
    )

    readonly_fields = (
        'request_id',
        'user',
        'model',
        'temperature',
        'response_model_name',
        'system_prompt',
        'user_input',
        'user_input_length',
        'status',
        'response_data',
        'error_message',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'duration_ms',
        'created',
        'modified',
    )

    fieldsets = (
        ('Request Information', {
            'fields': (
                'request_id',
                'user',
                'created',
                'status',
            )
        }),
        ('Model Configuration', {
            'fields': (
                'model',
                'temperature',
                'response_model_name',
            )
        }),
        ('Prompt Data', {
            'fields': (
                'system_prompt',
                'user_input',
                'user_input_length',
            ),
            'classes': ('collapse',),
        }),
        ('Response Data', {
            'fields': (
                'response_data',
                'error_message',
            ),
            'classes': ('collapse',),
        }),
        ('Usage Metrics', {
            'fields': (
                'prompt_tokens',
                'completion_tokens',
                'total_tokens',
                'duration_ms',
            )
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup."""
        return request.user.is_superuser

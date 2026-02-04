"""User models admin."""
from typing import List

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Models
from api.users.models import *


class IdentityFilesInline(admin.StackedInline):
    model = IdentityFiles
    extra = 0


class CustomUserAdmin(UserAdmin):
    """User model admin."""
    inlines = [IdentityFilesInline]
    list_display = ('id', 'phone_number', 'username', 'first_name', 'last_name', 'is_staff',
                    'deleted', 'is_active', 'preferred_provider')
    search_fields: List[str] = ['phone_number', ]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'),
         {'fields': ('first_name', 'last_name', 'email', 'dob', 'phone_number', 'preferred_provider', 'wallet', 'recommendation')}),
        (_('Roles'), {'fields': ('role', 'is_first_investment')}),
        (_('Deleted'), {'fields': ('deleted',)}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_verified', 'verified_at', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'phone_number'),
        }),
    )


class BankInformationInline(admin.StackedInline):
    model = BankInformation
    extra = 0


class BankAdmin(admin.ModelAdmin):
    inlines = [BankInformationInline]


admin.site.register(BankAccountType)
admin.site.register(User, CustomUserAdmin)

admin.site.register(DocumentType)

admin.site.register(Bank, BankAdmin)


@admin.register(ExternalAuthenticationToken)
class ExternalAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'type', 'user',)

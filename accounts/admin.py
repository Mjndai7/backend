from django.contrib import admin

# Register your models here.
from .models import Users

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



class UserAdmin(BaseUserAdmin):
    # The fields are populating the user models.
    list_display = ["uid", 'email', "username", "is_admin"]
    list_filter = ["is_admin"]
    field_sets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["username"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "username", "password", "password2"]
            },
        ),

    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []

admin.site.register(Users, UserAdmin)

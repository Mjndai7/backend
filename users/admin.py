from django.contrib import admin

# Register your models here.
from .models import UserAccount

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



class UserAdmin(BaseUserAdmin):
    # The fields are populating the user models.
    list_display = ["uid", 'email', "is_superuser", "first_name", "last_name"]
    list_filter = ["is_superuser"]
    field_sets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name"]}),
        ("Permissions", {"fields": ["is_superuser"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email",  "password", "first_name", "last_name"]
            },
        ),

    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []

admin.site.register(UserAccount, UserAdmin)

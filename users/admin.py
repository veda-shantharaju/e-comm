from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser,Address

# Register your models here.

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1  # Allows adding one new address by default
    
class CustomUserAdmin(UserAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",  # Added phone_number here
        "is_active",
        "is_staff",
    ]
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {"fields": ("phone_number",)},  # Added phone_number to existing fieldsets
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "groups",
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",  # Added phone_number here
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
    ordering = ("id",)
    inlines = [AddressInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Address)
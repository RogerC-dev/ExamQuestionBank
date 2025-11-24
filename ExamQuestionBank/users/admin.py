from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Subscription, Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Extend base config so autocomplete/search works with flashcard admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Subscription', {'fields': ('is_admin',)}),
    )
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_admin')
    search_fields = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'status', 'starts_at', 'expires_at')
    list_filter = ('tier', 'status')
    search_fields = ('user__username', 'user__email')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('subscription__user__username', 'transaction_id')

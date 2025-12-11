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
    list_filter = ('is_staff', 'is_admin', 'is_superuser', 'is_active')
    actions = ['make_admin', 'remove_admin', 'make_staff', 'remove_staff']

    @admin.action(description='設為管理員 (is_admin + is_staff)')
    def make_admin(self, request, queryset):
        updated = queryset.update(is_admin=True, is_staff=True)
        self.message_user(request, f'已將 {updated} 個使用者設為管理員')

    @admin.action(description='移除管理員權限')
    def remove_admin(self, request, queryset):
        updated = queryset.update(is_admin=False, is_staff=False)
        self.message_user(request, f'已移除 {updated} 個使用者的管理員權限')

    @admin.action(description='設為 Staff (可登入後台)')
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'已將 {updated} 個使用者設為 Staff')

    @admin.action(description='移除 Staff 權限')
    def remove_staff(self, request, queryset):
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'已移除 {updated} 個使用者的 Staff 權限')


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

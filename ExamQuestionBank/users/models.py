from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    使用者
    """
    email = models.EmailField(unique=True, verbose_name="電子郵件")
    is_admin = models.BooleanField(default=False, verbose_name="是否為管理員")

    class Meta:
        db_table = 'user'
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

    def __str__(self):
        return self.username

    @property
    def has_active_subscription(self):
        """檢查是否有有效的訂閱"""
        return self.subscriptions.filter(
            status='active',
            expires_at__gt=timezone.now()
        ).exists()

    @property
    def subscription_tier(self):
        """取得訂閱等級"""
        active_sub = self.subscriptions.filter(
            status='active',
            expires_at__gt=timezone.now()
        ).first()
        return active_sub.tier if active_sub else 'free'


class Subscription(models.Model):
    """訂閱"""
    TIER_CHOICES = [
        ('free', '免費版'),
        ('premium', '進階版'),
    ]

    STATUS_CHOICES = [
        ('active', '有效'),
        ('cancelled', '已取消'),
        ('expired', '已過期'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free', verbose_name="訂閱等級")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="狀態")
    starts_at = models.DateTimeField(auto_now_add=True, verbose_name="開始時間")
    expires_at = models.DateTimeField(verbose_name="到期時間")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription'
        verbose_name = '訂閱'
        verbose_name_plural = '訂閱'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_tier_display()}"

    def is_active(self):
        """檢查訂閱是否有效"""
        return self.status == 'active' and self.expires_at > timezone.now()


class Payment(models.Model):
    """付款記錄"""
    STATUS_CHOICES = [
        ('pending', '待處理'),
        ('completed', '已完成'),
        ('failed', '失敗'),
        ('refunded', '已退款'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="金額")
    currency = models.CharField(max_length=3, default='TWD', verbose_name="幣別")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    payment_method = models.CharField(max_length=50, verbose_name="付款方式")
    transaction_id = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="交易ID")
    stripe_payment_intent_id = models.CharField(max_length=200, null=True, blank=True, verbose_name="Stripe Payment Intent ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment'
        verbose_name = '付款記錄'
        verbose_name_plural = '付款記錄'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount} {self.currency}"
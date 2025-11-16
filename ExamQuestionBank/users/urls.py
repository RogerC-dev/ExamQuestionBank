from django.urls import path
from .subscription_views import SubscriptionStatusView, CreateSubscriptionView, CancelSubscriptionView

urlpatterns = [
    path('subscription/status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('subscription/create/', CreateSubscriptionView.as_view(), name='subscription_create'),
    path('subscription/cancel/', CancelSubscriptionView.as_view(), name='subscription_cancel'),
]


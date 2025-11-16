from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Subscription, Payment, User


class SubscriptionStatusView(APIView):
    """
    訂閱狀態 API
    GET /api/v1/subscription/status - 取得訂閱狀態
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得訂閱狀態",
        operation_description="取得當前使用者的訂閱狀態",
        responses={200: '成功'}
    )
    def get(self, request):
        user = request.user
        active_subscription = Subscription.objects.filter(
            user=user,
            status='active',
            expires_at__gt=timezone.now()
        ).first()

        if active_subscription:
            return Response({
                'tier': active_subscription.tier,
                'status': active_subscription.status,
                'expires_at': active_subscription.expires_at.isoformat(),
                'is_active': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'tier': 'free',
                'status': 'free',
                'expires_at': None,
                'is_active': False
            }, status=status.HTTP_200_OK)


class CreateSubscriptionView(APIView):
    """
    建立訂閱 API
    POST /api/v1/subscription/create - 建立新訂閱
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="建立訂閱",
        operation_description="建立新的訂閱（需要先完成付款）",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tier', 'payment_intent_id'],
            properties={
                'tier': openapi.Schema(type=openapi.TYPE_STRING, enum=['premium'], description='訂閱等級'),
                'payment_intent_id': openapi.Schema(type=openapi.TYPE_STRING, description='Stripe Payment Intent ID'),
            }
        ),
        responses={
            201: '訂閱建立成功',
            400: '請求參數錯誤'
        }
    )
    def post(self, request):
        tier = request.data.get('tier')
        payment_intent_id = request.data.get('payment_intent_id')

        if tier not in ['premium']:
            return Response(
                {"error": "無效的訂閱等級"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not payment_intent_id:
            return Response(
                {"error": "請提供付款資訊"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: 驗證 Stripe Payment Intent
        # 這裡應該呼叫 Stripe API 驗證付款是否成功
        # 目前先假設付款成功

        # 取消現有的訂閱
        Subscription.objects.filter(
            user=request.user,
            status='active'
        ).update(status='cancelled')

        # 建立新訂閱（1個月）
        expires_at = timezone.now() + timedelta(days=30)
        subscription = Subscription.objects.create(
            user=request.user,
            tier=tier,
            status='active',
            expires_at=expires_at
        )

        # 建立付款記錄
        Payment.objects.create(
            subscription=subscription,
            amount=500.00,  # NT$ 500
            currency='TWD',
            status='completed',
            payment_method='stripe',
            stripe_payment_intent_id=payment_intent_id,
            transaction_id=payment_intent_id
        )

        return Response({
            'subscription_id': subscription.id,
            'tier': subscription.tier,
            'expires_at': subscription.expires_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class CancelSubscriptionView(APIView):
    """
    取消訂閱 API
    POST /api/v1/subscription/cancel - 取消訂閱
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取消訂閱",
        operation_description="取消當前有效的訂閱",
        responses={
            200: '訂閱已取消',
            404: '找不到有效訂閱'
        }
    )
    def post(self, request):
        active_subscription = Subscription.objects.filter(
            user=request.user,
            status='active',
            expires_at__gt=timezone.now()
        ).first()

        if not active_subscription:
            return Response(
                {"error": "找不到有效訂閱"},
                status=status.HTTP_404_NOT_FOUND
            )

        active_subscription.status = 'cancelled'
        active_subscription.save()

        return Response({
            'message': '訂閱已取消',
            'subscription_id': active_subscription.id
        }, status=status.HTTP_200_OK)


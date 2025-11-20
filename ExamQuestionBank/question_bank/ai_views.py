import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .services.ai_service import ai_service
from .models import AIChatHistory, Question
from users.models import User

logger = logging.getLogger(__name__)

class AIChatView(APIView):
    """
    AI 聊天 API
    POST /api/v1/ai/chat - 發送訊息給 AI
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="AI 聊天",
        operation_description="發送訊息給 AI 並取得回應",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='使用者訊息'),
                'context_type': openapi.Schema(type=openapi.TYPE_STRING, description='上下文類型（如：question, case）'),
                'context_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='上下文ID（如題目ID）'),
            }
        ),
        responses={
            200: openapi.Response(
                description='成功',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'response': openapi.Schema(type=openapi.TYPE_STRING, description='AI 回應'),
                        'chat_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='聊天記錄ID'),
                    }
                )
            ),
            400: '請求參數錯誤',
            429: '達到每日使用限制',
            500: '伺服器錯誤'
        }
    )
    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response(
                    {"error": "請提供訊息內容"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 檢查使用限制（免費版每日10次）
            user = request.user
            if not self._check_usage_limit(user):
                return Response(
                    {"error": "已達到每日 AI 聊天使用限制（10次），請升級至進階版以獲得無限使用"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # 建立上下文
            context = None
            context_type = request.data.get('context_type')
            context_id = request.data.get('context_id')

            if context_type == 'question' and context_id:
                try:
                    question = Question.objects.get(id=context_id)
                    context = {
                        'question_id': question.id,
                        'question_content': question.content,
                        'related_laws': [tag.name for tag in question.tags.all()[:5]]
                    }
                except Question.DoesNotExist:
                    logger.warning(f"Question not found for context_id: {context_id}")

            # 呼叫 AI 服務
            ai_response = ai_service.chat(message, context)

            # 儲存聊天記錄
            chat_history = AIChatHistory.objects.create(
                user=user,
                message=message,
                response=ai_response,
                context_type=context_type,
                context_id=context_id
            )

            return Response({
                "response": ai_response,
                "chat_id": chat_history.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in AIChatView: {str(e)}", exc_info=True)
            return Response(
                {"error": "處理請求時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _check_usage_limit(self, user) -> bool:
        """
        檢查使用者是否達到使用限制
        免費版：每日10次
        進階版：無限制
        """
        try:
            # 檢查使用者訂閱狀態
            if hasattr(user, 'has_active_subscription') and user.has_active_subscription:
                # 進階版無限制
                if user.subscription_tier == 'premium':
                    return True

            # 管理員無限制
            if hasattr(user, 'is_admin') and user.is_admin:
                return True

            # 檢查今日使用次數
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = AIChatHistory.objects.filter(
                user=user,
                created_at__gte=today_start
            ).count()

            # 免費版限制：10次/日
            free_limit = 10
            return today_count < free_limit

        except Exception as e:
            logger.error(f"Error checking usage limit: {str(e)}")
            # 發生錯誤時保守起見，允許訪問（或根據需求拒絕）
            return True


class AIChatHistoryView(APIView):
    """
    AI 聊天記錄 API
    GET /api/v1/ai/history - 取得聊天記錄
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得 AI 聊天記錄",
        operation_description="取得使用者的 AI 聊天記錄",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description='返回記錄數量',
                type=openapi.TYPE_INTEGER,
                default=20
            ),
            openapi.Parameter(
                'offset',
                openapi.IN_QUERY,
                description='偏移量',
                type=openapi.TYPE_INTEGER,
                default=0
            ),
        ],
        responses={200: '成功'}
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))

            histories = AIChatHistory.objects.filter(
                user=request.user
            ).order_by('-created_at')[offset:offset + limit]

            data = [{
                'id': h.id,
                'message': h.message,
                'response': h.response,
                'context_type': h.context_type,
                'context_id': h.context_id,
                'created_at': h.created_at.isoformat()
            } for h in histories]

            return Response({
                'count': len(data),
                'results': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching chat history: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得聊天記錄失敗"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIAnalyzeCaseView(APIView):
    """
    AI 案例分析 API
    POST /api/v1/ai/analyze-case - 分析案例文字
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="AI 案例分析",
        operation_description="分析法律案例文字，提取關鍵點和相關法條",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['case_text'],
            properties={
                'case_text': openapi.Schema(type=openapi.TYPE_STRING, description='案例文字'),
            }
        ),
        responses={
            200: '成功',
            400: '參數錯誤',
            429: '達到使用限制',
            500: '伺服器錯誤'
        }
    )
    def post(self, request):
        try:
            case_text = request.data.get('case_text')
            if not case_text:
                return Response(
                    {"error": "請提供案例文字"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 檢查使用限制
            # 這裡重複使用了 AIChatView 的檢查邏輯，或許可以提取為 mixin 或 decorator
            user = request.user
            if not AIChatView()._check_usage_limit(user):
                return Response(
                    {"error": "已達到每日 AI 使用限制，請升級至進階版"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # 分析案例
            analysis = ai_service.analyze_case(case_text)

            # 儲存為聊天記錄
            AIChatHistory.objects.create(
                user=user,
                message=f"[案例分析] {case_text[:100]}...",
                response=f"摘要：{analysis['summary']}\n關鍵點：{', '.join(analysis['key_points'])}\n相關法條：{', '.join(analysis['related_laws'])}",
                context_type='case'
            )

            return Response(analysis, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error analyzing case: {str(e)}", exc_info=True)
            return Response(
                {"error": "分析案例時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .services.ai_service import ai_service
from .models import EssayAnalysisChat, AIChatHistory

logger = logging.getLogger(__name__)

# 申論解析專用 prompt
ESSAY_ANALYSIS_SYSTEM_PROMPT = """你是一位專業的台灣司法官/律師考試申論題解析助手。

當學生貼上一道申論題時，你需要提供以下分析（請用簡潔的格式）：

【可能涉及的法條】
列出 3-5 條最相關的法條，格式：法律名稱 第X條

【學說見解】
簡述主要學說觀點（1-2句）

【實務見解】
簡述實務判例/判決見解（1-2句）

【答題架構參考】
提供一個簡短的答題開頭模板，例如：
「本題涉及刑法第XXX條之○○罪。甲之行為是否該當該條所定之...，學說上有...，實務上則以...，學生以為...」

注意：
- 回答要簡潔，不要太詳細，只是給學生一個起點
- 用繁體中文
- 如果題目不清楚是哪個法律領域，請先判斷可能的領域再分析"""


class EssayAnalysisView(APIView):
    """
    申論解析 API
    POST /api/v1/essay-analysis/analyze - 分析申論題
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="申論題解析",
        operation_description="分析申論題並提供答題架構參考",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['question_text'],
            properties={
                'question_text': openapi.Schema(type=openapi.TYPE_STRING, description='申論題目內容'),
            }
        ),
        responses={
            200: openapi.Response(
                description='成功',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'analysis': openapi.Schema(type=openapi.TYPE_STRING, description='AI 解析'),
                        'chat_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='記錄ID'),
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
            question_text = request.data.get('question_text')
            if not question_text:
                return Response(
                    {"error": "請提供申論題目內容"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = request.user
            if not self._check_usage_limit(user):
                return Response(
                    {"error": "已達到每日 AI 使用限制（10次），請升級至進階版"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # 呼叫 AI 服務
            analysis = self._analyze_essay_question(question_text)

            # 儲存記錄（除非是錯誤訊息）
            chat_id = None
            if not self._is_error_response(analysis):
                chat_record = EssayAnalysisChat.objects.create(
                    user=user,
                    question_text=question_text,
                    analysis_response=analysis
                )
                chat_id = chat_record.id

            return Response({
                "analysis": analysis,
                "chat_id": chat_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in EssayAnalysisView: {str(e)}", exc_info=True)
            return Response(
                {"error": "處理請求時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _analyze_essay_question(self, question_text: str) -> str:
        """使用專用 prompt 分析申論題"""
        if not ai_service.is_configured():
            return "AI 服務尚未設定，請聯繫管理員。"

        try:
            messages = [
                {"role": "system", "content": ESSAY_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": f"請分析以下申論題：\n\n{question_text}"}
            ]

            response = ai_service.client.chat.completions.create(
                model=ai_service.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error analyzing essay question: {str(e)}")
            return "分析時發生錯誤，請稍後再試。"

    def _check_usage_limit(self, user) -> bool:
        """檢查使用限制"""
        try:
            if hasattr(user, 'is_admin') and user.is_admin:
                return True
            if hasattr(user, 'has_active_subscription') and user.has_active_subscription:
                if user.subscription_tier == 'premium':
                    return True

            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # 合併計算 AI chat 和 essay analysis 的使用次數
            ai_count = AIChatHistory.objects.filter(user=user, created_at__gte=today_start).count()
            essay_count = EssayAnalysisChat.objects.filter(user=user, created_at__gte=today_start).count()
            return (ai_count + essay_count) < 10
        except Exception as e:
            logger.error(f"Error checking usage limit: {str(e)}")
            return True

    def _is_error_response(self, response: str) -> bool:
        """
        檢查回應是否為錯誤訊息
        """
        error_patterns = [
            '錯誤',
            '失敗',
            '請稍後再試',
            'error',
            'failed',
        ]
        response_lower = response.lower() if response else ''
        return any(pattern in response_lower for pattern in error_patterns)


class EssayAnalysisHistoryView(APIView):
    """
    申論解析記錄 API
    GET /api/v1/essay-analysis/history - 取得解析記錄
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得申論解析記錄",
        operation_description="取得使用者的申論解析記錄",
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description='返回記錄數量', type=openapi.TYPE_INTEGER, default=20),
            openapi.Parameter('offset', openapi.IN_QUERY, description='偏移量', type=openapi.TYPE_INTEGER, default=0),
        ],
        responses={200: '成功'}
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))

            records = EssayAnalysisChat.objects.filter(
                user=request.user
            ).order_by('-created_at')[offset:offset + limit]

            data = [{
                'id': r.id,
                'question_text': r.question_text,
                'analysis_response': r.analysis_response,
                'created_at': r.created_at.isoformat()
            } for r in records]

            return Response({
                'count': len(data),
                'results': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching essay analysis history: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得記錄失敗"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

"""
申論題提交與批改 API
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db import transaction

from .models import EssaySubmission, EssayGrading, Subject
from .serializers import EssaySubmissionSerializer, EssaySubmissionCreateSerializer, EssayGradingSerializer
from .services.ai_service import ai_service
from .services.rag_service import rag_service

logger = logging.getLogger(__name__)


class EssaySubmissionPagination(PageNumberPagination):
    """申論題提交分頁"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class EssaySubmissionView(APIView):
    """
    申論題提交 API
    POST /api/v1/essays/submit/ - 提交申論題答案
    GET /api/v1/essays/ - 取得使用者的申論題列表
    """
    permission_classes = [IsAuthenticated]
    pagination_class = EssaySubmissionPagination

    @swagger_auto_schema(
        operation_summary="提交申論題答案",
        operation_description="提交申論題答案，系統將使用 AI 進行批改",
        request_body=EssaySubmissionCreateSerializer,
        responses={
            201: EssaySubmissionSerializer(),
            400: '請求參數錯誤',
            500: '伺服器錯誤'
        }
    )
    def post(self, request):
        """提交申論題答案"""
        try:
            serializer = EssaySubmissionCreateSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)

            # 創建提交記錄
            essay_submission = serializer.save()

            # 異步觸發 AI 批改（這裡先同步處理，後續可改為異步）
            self._grade_essay_async(essay_submission.id)

            response_serializer = EssaySubmissionSerializer(essay_submission)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error submitting essay: {str(e)}", exc_info=True)
            return Response(
                {"error": "提交申論題時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="取得申論題列表",
        operation_description="取得使用者的所有申論題提交記錄",
        manual_parameters=[
            openapi.Parameter(
                'subject',
                openapi.IN_QUERY,
                description='科目 ID 篩選',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='狀態篩選 (pending/grading/completed)',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description='頁碼',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ],
        responses={200: EssaySubmissionSerializer(many=True)}
    )
    def get(self, request):
        """取得申論題列表"""
        try:
            queryset = EssaySubmission.objects.filter(user=request.user).select_related(
                'subject', 'exam_session'
            ).prefetch_related('grading').order_by('-submitted_at')

            # 篩選
            subject_id = request.query_params.get('subject')
            if subject_id:
                queryset = queryset.filter(subject_id=subject_id)

            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            # 分頁
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)

            if page is not None:
                serializer = EssaySubmissionSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = EssaySubmissionSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching essays: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得申論題列表時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _grade_essay_async(self, essay_submission_id: int):
        """
        異步批改申論題（目前為同步實現，後續可改為 Celery 任務）
        """
        try:
            essay_submission = EssaySubmission.objects.get(id=essay_submission_id)
            
            # 更新狀態為批改中
            essay_submission.status = 'grading'
            essay_submission.save()

            # 獲取 RAG 上下文
            subject_name = essay_submission.subject.name if essay_submission.subject else "未知科目"
            rag_context = None
            if rag_service.is_configured():
                rag_context = rag_service.get_context_for_essay_grading(
                    subject=subject_name,
                    question_text=essay_submission.question_text,
                    answer_text=essay_submission.answer_text
                )

            # 使用 AI 批改
            grading_result = ai_service.grade_essay(
                subject=subject_name,
                question_text=essay_submission.question_text,
                answer_text=essay_submission.answer_text,
                rag_context=rag_context
            )

            # 保存批改結果
            with transaction.atomic():
                grading = EssayGrading.objects.create(
                    essay_submission=essay_submission,
                    score=grading_result.get('score', 0),
                    max_score=grading_result.get('max_score', 100.0),
                    feedback=grading_result.get('feedback', ''),
                    strengths='\n'.join(grading_result.get('strengths', [])),
                    weaknesses='\n'.join(grading_result.get('weaknesses', [])),
                    suggestions='\n'.join(grading_result.get('suggestions', [])),
                    grading_method='ai'
                )

                # 更新提交狀態
                essay_submission.status = 'completed'
                essay_submission.save()

            logger.info(f"Essay {essay_submission_id} graded successfully")

        except EssaySubmission.DoesNotExist:
            logger.error(f"Essay submission {essay_submission_id} not found")
        except Exception as e:
            logger.error(f"Error grading essay {essay_submission_id}: {str(e)}", exc_info=True)
            # 更新狀態為錯誤（可選）
            try:
                essay_submission = EssaySubmission.objects.get(id=essay_submission_id)
                essay_submission.status = 'pending'  # 或創建一個 'error' 狀態
                essay_submission.save()
            except:
                pass


class EssayDetailView(APIView):
    """
    申論題詳細資訊 API
    GET /api/v1/essays/{id}/ - 取得申論題詳細資訊
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得申論題詳細資訊",
        operation_description="取得指定申論題的詳細資訊和批改結果",
        responses={
            200: EssaySubmissionSerializer(),
            404: '申論題不存在',
            403: '無權限訪問'
        }
    )
    def get(self, request, pk):
        """取得申論題詳細資訊"""
        try:
            essay_submission = EssaySubmission.objects.select_related(
                'subject', 'exam_session'
            ).prefetch_related('grading').get(id=pk, user=request.user)

            serializer = EssaySubmissionSerializer(essay_submission)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except EssaySubmission.DoesNotExist:
            return Response(
                {"error": "申論題不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching essay detail: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得申論題詳細資訊時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EssayGradingView(APIView):
    """
    申論題批改結果 API
    GET /api/v1/essays/{id}/grading/ - 取得批改結果
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得批改結果",
        operation_description="取得指定申論題的批改結果",
        responses={
            200: EssayGradingSerializer(),
            404: '批改結果不存在'
        }
    )
    def get(self, request, pk):
        """取得批改結果"""
        try:
            essay_submission = EssaySubmission.objects.get(id=pk, user=request.user)

            if not hasattr(essay_submission, 'grading'):
                return Response(
                    {"error": "批改結果尚未生成"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = EssayGradingSerializer(essay_submission.grading)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except EssaySubmission.DoesNotExist:
            return Response(
                {"error": "申論題不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching grading: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得批改結果時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




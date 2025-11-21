"""
學習進度分析與建議 API
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Q, Sum, FloatField
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    Question, UserProgress, StudySession, StudyRecommendation,
    Subject, Attempt, EssaySubmission
)
from .services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ProgressAnalyticsView(APIView):
    """
    學習進度分析 API
    GET /api/v1/analytics/progress/ - 取得整體學習進度
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得學習進度",
        operation_description="取得使用者的整體學習進度統計",
        manual_parameters=[
            openapi.Parameter(
                'time_range',
                openapi.IN_QUERY,
                description='時間範圍 (7/30/90/all)',
                type=openapi.TYPE_STRING,
                required=False,
                default='all'
            ),
        ],
        responses={200: '成功'}
    )
    def get(self, request):
        """取得學習進度"""
        try:
            user = request.user
            time_range = request.query_params.get('time_range', 'all')

            # 計算時間範圍
            date_filter = None
            if time_range != 'all':
                days = int(time_range)
                date_filter = timezone.now() - timedelta(days=days)

            # 總題數
            total_questions = Question.objects.count()

            # 已練習題數
            if date_filter:
                practiced_questions = UserProgress.objects.filter(
                    user=user,
                    last_attempt_at__gte=date_filter
                ).values('question').distinct().count()
            else:
                practiced_questions = UserProgress.objects.filter(
                    user=user
                ).values('question').distinct().count()

            # 總嘗試次數
            if date_filter:
                total_attempts = UserProgress.objects.filter(
                    user=user,
                    last_attempt_at__gte=date_filter
                ).count()
            else:
                total_attempts = UserProgress.objects.filter(user=user).count()

            # 正確次數
            if date_filter:
                correct_attempts = UserProgress.objects.filter(
                    user=user,
                    is_correct=True,
                    last_attempt_at__gte=date_filter
                ).count()
            else:
                correct_attempts = UserProgress.objects.filter(
                    user=user,
                    is_correct=True
                ).count()

            # 計算正確率
            accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

            # 計算進度百分比
            progress_percentage = (practiced_questions / total_questions * 100) if total_questions > 0 else 0

            # 每日趨勢（最近30天）
            trend_days = 30
            trend_start = timezone.now() - timedelta(days=trend_days)
            daily_progress = UserProgress.objects.filter(
                user=user,
                last_attempt_at__gte=trend_start
            ).annotate(
                date=TruncDate('last_attempt_at')
            ).values('date').annotate(
                attempts=Count('id'),
                correct=Count('id', filter=Q(is_correct=True))
            ).order_by('date')

            trend_data = []
            for item in daily_progress:
                daily_accuracy = (item['correct'] / item['attempts'] * 100) if item['attempts'] > 0 else 0
                trend_data.append({
                    'date': item['date'].isoformat() if item['date'] else None,
                    'attempts': item['attempts'],
                    'correct': item['correct'],
                    'accuracy': round(daily_accuracy, 2)
                })

            return Response({
                'overall': {
                    'total_questions': total_questions,
                    'practiced_questions': practiced_questions,
                    'progress_percentage': round(progress_percentage, 2),
                    'total_attempts': total_attempts,
                    'correct_attempts': correct_attempts,
                    'accuracy': round(accuracy, 2)
                },
                'trend': trend_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching progress: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得學習進度時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubjectBreakdownView(APIView):
    """
    科目分析 API
    GET /api/v1/analytics/subjects/ - 取得科目別學習統計
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得科目分析",
        operation_description="取得各科目的學習統計數據",
        responses={200: '成功'}
    )
    def get(self, request):
        """取得科目分析"""
        try:
            user = request.user

            # 取得所有科目
            subjects = Subject.objects.all()

            subject_stats = []
            for subject in subjects:
                # 該科目的進度記錄
                progress_records = UserProgress.objects.filter(
                    user=user,
                    subject=subject
                )

                if not progress_records.exists():
                    continue

                # 統計數據
                practiced_count = progress_records.values('question').distinct().count()
                total_attempts = progress_records.count()
                correct_attempts = progress_records.filter(is_correct=True).count()
                accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

                # 平均時間
                avg_time = progress_records.aggregate(
                    avg_time=Avg('time_spent')
                )['avg_time'] or 0

                subject_stats.append({
                    'subject_id': subject.id,
                    'subject_name': subject.name,
                    'subject_code': subject.code,
                    'practiced': practiced_count,
                    'total_attempts': total_attempts,
                    'correct_attempts': correct_attempts,
                    'accuracy': round(accuracy, 2),
                    'avg_time_spent': round(avg_time, 2)
                })

            # 按正確率排序
            subject_stats.sort(key=lambda x: x['accuracy'], reverse=True)

            return Response({
                'subjects': subject_stats,
                'total_subjects': len(subject_stats)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching subject breakdown: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得科目分析時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrendsView(APIView):
    """
    學習趨勢 API
    GET /api/v1/analytics/trends/ - 取得學習趨勢數據
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得學習趨勢",
        operation_description="取得學習趨勢數據（正確率、答題量等）",
        manual_parameters=[
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description='天數 (預設30)',
                type=openapi.TYPE_INTEGER,
                required=False,
                default=30
            ),
        ],
        responses={200: '成功'}
    )
    def get(self, request):
        """取得學習趨勢"""
        try:
            user = request.user
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)

            # 每日統計
            daily_stats = UserProgress.objects.filter(
                user=user,
                last_attempt_at__gte=start_date
            ).annotate(
                date=TruncDate('last_attempt_at')
            ).values('date').annotate(
                attempts=Count('id'),
                correct=Count('id', filter=Q(is_correct=True)),
                avg_time=Avg('time_spent')
            ).order_by('date')

            trend_data = []
            for stat in daily_stats:
                accuracy = (stat['correct'] / stat['attempts'] * 100) if stat['attempts'] > 0 else 0
                trend_data.append({
                    'date': stat['date'].isoformat() if stat['date'] else None,
                    'attempts': stat['attempts'],
                    'correct': stat['correct'],
                    'accuracy': round(accuracy, 2),
                    'avg_time_spent': round(stat['avg_time'] or 0, 2)
                })

            # 計算整體趨勢
            recent_days = days // 2
            recent_start = timezone.now() - timedelta(days=recent_days)
            earlier_start = timezone.now() - timedelta(days=days)

            recent_accuracy = UserProgress.objects.filter(
                user=user,
                last_attempt_at__gte=recent_start
            ).aggregate(
                accuracy=Avg('is_correct', output_field=FloatField()) * 100
            )['accuracy'] or 0

            earlier_accuracy = UserProgress.objects.filter(
                user=user,
                last_attempt_at__gte=earlier_start,
                last_attempt_at__lt=recent_start
            ).aggregate(
                accuracy=Avg('is_correct', output_field=FloatField()) * 100
            )['accuracy'] or 0

            trend_direction = 'improving' if recent_accuracy > earlier_accuracy else 'declining' if recent_accuracy < earlier_accuracy else 'stable'

            return Response({
                'trend_data': trend_data,
                'trend_direction': trend_direction,
                'recent_accuracy': round(recent_accuracy, 2),
                'earlier_accuracy': round(earlier_accuracy, 2)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching trends: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得學習趨勢時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendationsView(APIView):
    """
    學習建議 API
    GET /api/v1/analytics/recommendations/ - 取得 AI 生成的學習建議
    POST /api/v1/analytics/recommendations/generate/ - 生成新的學習建議
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得學習建議",
        operation_description="取得使用者的學習建議列表",
        manual_parameters=[
            openapi.Parameter(
                'is_read',
                openapi.IN_QUERY,
                description='是否已讀 (true/false)',
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'priority',
                openapi.IN_QUERY,
                description='優先級篩選',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={200: '成功'}
    )
    def get(self, request):
        """取得學習建議"""
        try:
            user = request.user
            queryset = StudyRecommendation.objects.filter(user=user).select_related('subject').order_by('-priority', '-generated_at')

            # 篩選
            is_read = request.query_params.get('is_read')
            if is_read is not None:
                is_read_bool = is_read.lower() == 'true'
                queryset = queryset.filter(is_read=is_read_bool)

            priority = request.query_params.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)

            # 序列化
            from .serializers import StudyRecommendationSerializer
            serializer = StudyRecommendationSerializer(queryset, many=True)

            return Response({
                'count': len(serializer.data),
                'results': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching recommendations: {str(e)}", exc_info=True)
            return Response(
                {"error": "取得學習建議時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="生成學習建議",
        operation_description="使用 AI 分析學習進度並生成新的學習建議",
        responses={
            200: '成功',
            500: '生成失敗'
        }
    )
    def post(self, request):
        """生成學習建議"""
        try:
            user = request.user

            # 收集進度數據
            progress_data = self._collect_progress_data(user)

            # 使用 AI 分析
            analysis_result = ai_service.analyze_progress(progress_data)

            # 創建建議記錄
            from .models import StudyRecommendation
            recommendations = []

            # 總體建議
            if analysis_result.get('summary'):
                recommendation = StudyRecommendation.objects.create(
                    user=user,
                    recommendation_type='practice_schedule',
                    priority='high',
                    content=analysis_result['summary']
                )
                recommendations.append(recommendation)

            # 具體建議
            for rec_text in analysis_result.get('recommendations', []):
                recommendation = StudyRecommendation.objects.create(
                    user=user,
                    recommendation_type='practice_schedule',
                    priority='medium',
                    content=rec_text
                )
                recommendations.append(recommendation)

            # 重點科目建議
            for subject_name in analysis_result.get('focus_areas', []):
                try:
                    subject = Subject.objects.get(name=subject_name)
                    recommendation = StudyRecommendation.objects.create(
                        user=user,
                        subject=subject,
                        recommendation_type='subject_focus',
                        priority='high',
                        content=f"建議加強 {subject_name} 的練習"
                    )
                    recommendations.append(recommendation)
                except Subject.DoesNotExist:
                    pass

            from .serializers import StudyRecommendationSerializer
            serializer = StudyRecommendationSerializer(recommendations, many=True)

            return Response({
                'count': len(serializer.data),
                'results': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            return Response(
                {"error": "生成學習建議時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _collect_progress_data(self, user):
        """收集使用者進度數據"""
        # 總題數和已練習
        total_questions = Question.objects.count()
        practiced_questions = UserProgress.objects.filter(user=user).values('question').distinct().count()

        # 整體正確率
        total_attempts = UserProgress.objects.filter(user=user).count()
        correct_attempts = UserProgress.objects.filter(user=user, is_correct=True).count()
        accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

        # 科目分析
        subject_breakdown = {}
        subjects = Subject.objects.all()
        for subject in subjects:
            progress = UserProgress.objects.filter(user=user, subject=subject)
            if progress.exists():
                practiced = progress.values('question').distinct().count()
                correct = progress.filter(is_correct=True).count()
                total = progress.count()
                subj_accuracy = (correct / total * 100) if total > 0 else 0
                subject_breakdown[subject.name] = {
                    'practiced': practiced,
                    'accuracy': round(subj_accuracy, 2)
                }

        # 弱項科目（正確率低於平均）
        weak_areas = []
        if subject_breakdown:
            avg_accuracy = sum(s['accuracy'] for s in subject_breakdown.values()) / len(subject_breakdown)
            for subject_name, stats in subject_breakdown.items():
                if stats['accuracy'] < avg_accuracy - 10:  # 低於平均10%以上
                    weak_areas.append(subject_name)

        # 近期趨勢
        recent_days = 7
        recent_start = timezone.now() - timedelta(days=recent_days)
        recent_accuracy = UserProgress.objects.filter(
            user=user,
            last_attempt_at__gte=recent_start
        ).aggregate(
            accuracy=Avg('is_correct', output_field=models.FloatField()) * 100
        )['accuracy'] or 0

        earlier_start = timezone.now() - timedelta(days=recent_days * 2)
        earlier_accuracy = UserProgress.objects.filter(
            user=user,
            last_attempt_at__gte=earlier_start,
            last_attempt_at__lt=recent_start
        ).aggregate(
            accuracy=Avg('is_correct', output_field=models.FloatField()) * 100
        )['accuracy'] or 0

        recent_trend = 'improving' if recent_accuracy > earlier_accuracy else 'declining' if recent_accuracy < earlier_accuracy else 'stable'

        return {
            'total_questions': total_questions,
            'practiced_questions': practiced_questions,
            'accuracy': round(accuracy, 2),
            'subject_breakdown': subject_breakdown,
            'weak_areas': weak_areas,
            'recent_trend': recent_trend
        }


class MarkRecommendationReadView(APIView):
    """
    標記建議為已讀 API
    PATCH /api/v1/analytics/recommendations/{id}/read/ - 標記建議為已讀
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="標記建議為已讀",
        operation_description="將指定的學習建議標記為已讀",
        responses={
            200: '成功',
            404: '建議不存在'
        }
    )
    def patch(self, request, pk):
        """標記建議為已讀"""
        try:
            recommendation = StudyRecommendation.objects.get(id=pk, user=request.user)
            recommendation.is_read = True
            recommendation.read_at = timezone.now()
            recommendation.save()

            from .serializers import StudyRecommendationSerializer
            serializer = StudyRecommendationSerializer(recommendation)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except StudyRecommendation.DoesNotExist:
            return Response(
                {"error": "建議不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error marking recommendation as read: {str(e)}", exc_info=True)
            return Response(
                {"error": "標記建議時發生錯誤"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


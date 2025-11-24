from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Bookmark, Question
from flashcards.models import Flashcard
from users.models import User


class ExtensionStatsView(APIView):
    """
    擴充功能統計 API
    GET /api/v1/extension/stats - 取得使用者統計資訊（供擴充功能使用）
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="取得擴充功能統計",
        operation_description="取得使用者的統計資訊，供 Chrome 擴充功能顯示",
        responses={200: '成功'}
    )
    def get(self, request):
        user = request.user

        # 統計資訊
        stats = {
            'bookmarks_count': Bookmark.objects.filter(user=user).count(),
            'flashcards_count': Flashcard.objects.filter(user=user).count(),
            'practice_count': user.attempts.count() if hasattr(user, 'attempts') else 0,
            'subscription_tier': user.subscription_tier if hasattr(user, 'subscription_tier') else 'free',
        }

        return Response(stats, status=status.HTTP_200_OK)


class SyncBookmarksView(APIView):
    """
    同步書籤 API
    POST /api/v1/extension/sync-bookmarks - 同步書籤
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="同步書籤",
        operation_description="從擴充功能同步書籤到網頁平台",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['bookmarks'],
            properties={
                'bookmarks': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'case_url': openapi.Schema(type=openapi.TYPE_STRING),
                            'case_title': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            }
        ),
        responses={200: '同步成功'}
    )
    def post(self, request):
        bookmarks_data = request.data.get('bookmarks', [])
        user = request.user

        synced_count = 0
        errors = []

        for bookmark_data in bookmarks_data:
            try:
                question_id = bookmark_data.get('question_id')
                if question_id:
                    # 如果提供題目ID，直接建立書籤
                    question = Question.objects.get(id=question_id)
                    Bookmark.objects.get_or_create(
                        user=user,
                        question=question
                    )
                    synced_count += 1
                else:
                    # 如果沒有題目ID，可能需要從案例URL建立書籤
                    # 這裡可以擴展為建立案例書籤
                    errors.append(f"缺少題目ID：{bookmark_data.get('case_url', 'unknown')}")
            except Question.DoesNotExist:
                errors.append(f"題目不存在：{question_id}")
            except Exception as e:
                errors.append(f"同步失敗：{str(e)}")

        return Response({
            'synced_count': synced_count,
            'errors': errors
        }, status=status.HTTP_200_OK)


class SyncFlashcardsView(APIView):
    """
    同步快閃卡 API
    POST /api/v1/extension/sync-flashcards - 同步快閃卡進度
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="同步快閃卡",
        operation_description="從擴充功能同步快閃卡進度到網頁平台",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['flashcards'],
            properties={
                'flashcards': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'last_reviewed': openapi.Schema(type=openapi.TYPE_STRING),
                            'next_review': openapi.Schema(type=openapi.TYPE_STRING),
                            'ease_factor': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'interval': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    )
                )
            }
        ),
        responses={200: '同步成功'}
    )
    def post(self, request):
        flashcards_data = request.data.get('flashcards', [])
        user = request.user

        synced_count = 0
        errors = []

        for flashcard_data in flashcards_data:
            try:
                question_id = flashcard_data.get('question_id')
                if not question_id:
                    errors.append("缺少題目ID")
                    continue

                question = Question.objects.get(id=question_id)
                
                # 取得或建立快閃卡
                flashcard, created = Flashcard.objects.get_or_create(
                    user=user,
                    question=question
                )

                # 更新進度
                from django.utils import timezone
                from datetime import datetime, date

                if flashcard_data.get('next_review'):
                    next_review = datetime.fromisoformat(
                        flashcard_data['next_review'].replace('Z', '+00:00')
                    )
                    flashcard.next_review_date = next_review.date()

                if flashcard_data.get('last_reviewed'):
                    last_reviewed = datetime.fromisoformat(
                        flashcard_data['last_reviewed'].replace('Z', '+00:00')
                    )
                    flashcard.last_reviewed_at = last_reviewed

                if flashcard_data.get('review_count') is not None:
                    flashcard.review_count = flashcard_data['review_count']

                if flashcard_data.get('ease_factor') is not None:
                    flashcard.ease_factor = flashcard_data['ease_factor']

                if flashcard_data.get('interval') is not None:
                    flashcard.interval = flashcard_data['interval']

                if flashcard_data.get('repetition') is not None:
                    flashcard.repetition = flashcard_data['repetition']

                if flashcard_data.get('status') in dict(Flashcard.STATUS_CHOICES):
                    flashcard.status = flashcard_data['status']

                flashcard.save()
                synced_count += 1

            except Question.DoesNotExist:
                errors.append(f"題目不存在：{question_id}")
            except Exception as e:
                errors.append(f"同步失敗：{str(e)}")

        return Response({
            'synced_count': synced_count,
            'errors': errors
        }, status=status.HTTP_200_OK)


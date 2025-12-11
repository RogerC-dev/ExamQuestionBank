from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Flashcard, FlashcardReviewLog
from .serializers import (
    FlashcardSerializer,
    FlashcardReviewSerializer,
    FlashcardReviewLogSerializer,
)
from .services import SpacedRepetitionService


class FlashcardViewSet(viewsets.ModelViewSet):
    """CRUD + spaced repetition review endpoints."""

    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # 關閉分頁，返回所有卡片
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = (
            Flashcard.objects
            .select_related('question', 'user')
            .filter(user=self.request.user)
        )

        status_filter = self.request.query_params.get('status')
        if status_filter == 'due':
            queryset = queryset.filter(next_review_date__lte=timezone.now().date())
        elif status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('next_review_date', 'id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def due(self, request):
        """Return cards that require review today or are overdue."""
        queryset = self.get_queryset().filter(next_review_date__lte=timezone.now().date())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Apply SM-2 algorithm after a user scores their recall."""
        flashcard = self.get_object()
        review_serializer = FlashcardReviewSerializer(data=request.data)
        review_serializer.is_valid(raise_exception=True)

        rating = review_serializer.validated_data['rating']
        outcome = SpacedRepetitionService.calculate_next_review(flashcard, rating)

        flashcard.ease_factor = outcome.ease_factor
        flashcard.interval = outcome.interval
        flashcard.repetition = outcome.repetition
        flashcard.next_review_date = outcome.next_review_date
        flashcard.status = outcome.status
        flashcard.last_reviewed_at = timezone.now()
        flashcard.review_count = (flashcard.review_count or 0) + 1
        flashcard.save(update_fields=[
            'ease_factor',
            'interval',
            'repetition',
            'next_review_date',
            'status',
            'last_reviewed_at',
            'review_count',
        ])

        FlashcardReviewLog.objects.create(
            flashcard=flashcard,
            user=request.user,
            rating=rating,
            review_interval=outcome.interval,
        )

        return Response(self.get_serializer(flashcard).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Return totals, due counts, streak, and completion percentage."""
        queryset = self.get_queryset()
        total = queryset.count()
        due = queryset.filter(next_review_date__lte=timezone.now().date()).count()
        completion = 0 if total == 0 else round(((total - due) / total) * 100, 2)

        streak = self._calculate_review_streak(request.user)
        next_due = queryset.order_by('next_review_date').first()

        data = {
            'total_cards': total,
            'due_cards': due,
            'completion_percent': completion,
            'review_streak': streak,
            'next_review_date': next_due.next_review_date if next_due else None,
        }

        return Response(data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Return recent review logs for streak and timeline visualizations."""
        logs = (
            FlashcardReviewLog.objects
            .filter(user=request.user)
            .select_related('flashcard')
            .order_by('-reviewed_at')[:50]
        )
        serializer = FlashcardReviewLogSerializer(logs, many=True)
        return Response(serializer.data)

    def _calculate_review_streak(self, user) -> int:
        """Count consecutive days with at least one review, ending today if applicable."""
        log_dates = set(
            FlashcardReviewLog.objects
            .filter(user=user)
            .values_list('reviewed_at__date', flat=True)
        )

        if not log_dates:
            return 0

        streak = 0
        current_day = timezone.now().date()

        while current_day in log_dates:
            streak += 1
            current_day -= timedelta(days=1)

        return streak

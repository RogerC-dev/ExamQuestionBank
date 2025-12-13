from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtractExamPDFView, ExtractAnswerPDFView, QuestionViewSet, SubjectListView, TagViewSet
from .ai_views import AIChatView, AIChatHistoryView, AIAnalyzeCaseView
from .essay_analysis_views import EssayAnalysisView, EssayAnalysisHistoryView
from .extension_views import ExtensionStatsView, SyncBookmarksView, SyncFlashcardsView
from .essay_views import EssaySubmissionView, EssayDetailView, EssayGradingView
from .analytics_views import (
    ProgressAnalyticsView, SubjectBreakdownView, TrendsView,
    RecommendationsView, MarkRecommendationReadView
)

# 建立 router 並註冊 ViewSet
router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path("subjects/", SubjectListView.as_view(), name="subjects"),
    path("extract-questions-pdf/", ExtractExamPDFView.as_view(), name="extract-questions_pdf"),
    path("extract-answers-pdf/", ExtractAnswerPDFView.as_view(), name="extract-answers_pdf"),
    # AI endpoints
    path("ai/chat/", AIChatView.as_view(), name="ai_chat"),
    path("ai/history/", AIChatHistoryView.as_view(), name="ai_history"),
    path("ai/analyze-case/", AIAnalyzeCaseView.as_view(), name="ai_analyze_case"),
    # Essay Analysis endpoints (separate from general AI chat)
    path("essay-analysis/analyze/", EssayAnalysisView.as_view(), name="essay_analysis"),
    path("essay-analysis/history/", EssayAnalysisHistoryView.as_view(), name="essay_analysis_history"),
    # Extension endpoints
    path("extension/stats/", ExtensionStatsView.as_view(), name="extension_stats"),
    path("extension/sync-bookmarks/", SyncBookmarksView.as_view(), name="extension_sync_bookmarks"),
    path("extension/sync-flashcards/", SyncFlashcardsView.as_view(), name="extension_sync_flashcards"),
    # Essay submission endpoints
    path("essays/submit/", EssaySubmissionView.as_view(), name="essay-submit"),
    path("essays/", EssaySubmissionView.as_view(), name="essay-list"),
    path("essays/<int:pk>/", EssayDetailView.as_view(), name="essay-detail"),
    path("essays/<int:pk>/grading/", EssayGradingView.as_view(), name="essay-grading"),
    # Analytics endpoints
    path("analytics/progress/", ProgressAnalyticsView.as_view(), name="analytics-progress"),
    path("analytics/subjects/", SubjectBreakdownView.as_view(), name="analytics-subjects"),
    path("analytics/trends/", TrendsView.as_view(), name="analytics-trends"),
    path("analytics/recommendations/", RecommendationsView.as_view(), name="analytics-recommendations"),
    path("analytics/recommendations/<int:pk>/read/", MarkRecommendationReadView.as_view(), name="analytics-recommendation-read"),
    # 包含 router 的 URL
    path("", include(router.urls)),
]

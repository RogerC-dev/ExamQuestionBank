from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtractExamPDFView, ExtractAnswerPDFView, QuestionViewSet
from .ai_views import AIChatView, AIChatHistoryView, AIAnalyzeCaseView
from .extension_views import ExtensionStatsView, SyncBookmarksView, SyncFlashcardsView

# 建立 router 並註冊 ViewSet
router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path("extract-questions-pdf/", ExtractExamPDFView.as_view(), name="extract-questions_pdf"),
    path("extract-answers-pdf/", ExtractAnswerPDFView.as_view(), name="extract-answers_pdf"),
    # AI endpoints
    path("ai/chat/", AIChatView.as_view(), name="ai_chat"),
    path("ai/history/", AIChatHistoryView.as_view(), name="ai_history"),
    path("ai/analyze-case/", AIAnalyzeCaseView.as_view(), name="ai_analyze_case"),
    # Extension endpoints
    path("extension/stats/", ExtensionStatsView.as_view(), name="extension_stats"),
    path("extension/sync-bookmarks/", SyncBookmarksView.as_view(), name="extension_sync_bookmarks"),
    path("extension/sync-flashcards/", SyncFlashcardsView.as_view(), name="extension_sync_flashcards"),
    # 包含 router 的 URL
    path("", include(router.urls)),
]
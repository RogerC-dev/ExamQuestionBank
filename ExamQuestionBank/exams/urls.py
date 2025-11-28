from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, MockExamView, MockExamDetailView, ExamResultView, ExamStatsView

# 建立 router 並註冊 ViewSet
router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    # 包含 router 的 URL
    path("", include(router.urls)),
    # 模擬測驗 API
    path("mock-exams/generate/", MockExamView.as_view(), name="mock-exam-generate"),
    path("mock-exams/", MockExamView.as_view(), name="mock-exam-list"),
    path("mock-exams/<int:pk>/", MockExamDetailView.as_view(), name="mock-exam-detail"),
    # 考試結果 API
    path("exam-results/", ExamResultView.as_view(), name="exam-results"),
    path("exam-stats/", ExamStatsView.as_view(), name="exam-stats"),
]

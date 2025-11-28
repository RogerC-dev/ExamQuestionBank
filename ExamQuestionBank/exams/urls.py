from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, MockExamView, MockExamDetailView, ExamResultView, ExamStatsView, WrongQuestionView, BookmarkView

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    path("", include(router.urls)),
    path("mock-exams/generate/", MockExamView.as_view(), name="mock-exam-generate"),
    path("mock-exams/", MockExamView.as_view(), name="mock-exam-list"),
    path("mock-exams/<int:pk>/", MockExamDetailView.as_view(), name="mock-exam-detail"),
    path("exam-results/", ExamResultView.as_view(), name="exam-results"),
    path("exam-stats/", ExamStatsView.as_view(), name="exam-stats"),
    path("wrong-questions/", WrongQuestionView.as_view(), name="wrong-questions"),
    path("wrong-questions/<int:pk>/", WrongQuestionView.as_view(), name="wrong-question-detail"),
    path("bookmarks/", BookmarkView.as_view(), name="bookmarks"),
    path("bookmarks/<int:pk>/", BookmarkView.as_view(), name="bookmark-detail"),
]

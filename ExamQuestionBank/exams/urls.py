from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamViewSet, ExamResultView, ExamStatsView, 
    WrongQuestionView, BookmarkView, CustomExamView
)

router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    path("exams/custom/", CustomExamView.as_view(), name="exam-custom"),
    path("", include(router.urls)),
    path("exam-results/", ExamResultView.as_view(), name="exam-results"),
    path("exam-stats/", ExamStatsView.as_view(), name="exam-stats"),
    path("wrong-questions/", WrongQuestionView.as_view(), name="wrong-questions"),
    path("wrong-questions/<int:pk>/", WrongQuestionView.as_view(), name="wrong-question-detail"),
    path("bookmarks/", BookmarkView.as_view(), name="bookmarks"),
    path("bookmarks/<int:pk>/", BookmarkView.as_view(), name="bookmark-detail"),
]

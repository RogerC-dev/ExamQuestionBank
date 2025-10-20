from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtractExamPDFView, ExtractAnswerPDFView, QuestionViewSet

# 建立 router 並註冊 ViewSet
router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path("extract-questions-pdf/", ExtractExamPDFView.as_view(), name="extract-questions_pdf"),
    path("extract-answers-pdf/", ExtractAnswerPDFView.as_view(), name="extract-answers_pdf"),
    # 包含 router 的 URL
    path("", include(router.urls)),
]
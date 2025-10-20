from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet

# 建立 router 並註冊 ViewSet
router = DefaultRouter()
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    # 包含 router 的 URL
    path("", include(router.urls)),
]

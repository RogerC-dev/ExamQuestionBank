from rest_framework.routers import DefaultRouter
from .views import StudyMetricViewSet, RecommendationViewSet, MockExamPerformanceViewSet

router = DefaultRouter()
router.register(r'analytics/metrics', StudyMetricViewSet, basename='study-metric')
router.register(r'analytics/recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'analytics/mock-performance', MockExamPerformanceViewSet, basename='mock-performance')

urlpatterns = router.urls


from rest_framework.routers import DefaultRouter
from .views import StudyMetricViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'analytics/metrics', StudyMetricViewSet, basename='study-metric')
router.register(r'analytics/recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = router.urls


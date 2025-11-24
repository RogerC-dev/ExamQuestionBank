from rest_framework.routers import DefaultRouter

from .views import (
    BadgeViewSet,
    UserBadgeViewSet,
    UserXPViewSet,
    StudyGroupViewSet,
    NotificationScheduleViewSet,
)

router = DefaultRouter()
router.register(r'gamification/badges', BadgeViewSet, basename='badge')
router.register(r'gamification/user-badges', UserBadgeViewSet, basename='user-badge')
router.register(r'gamification/user-xp', UserXPViewSet, basename='user-xp')
router.register(r'study-groups', StudyGroupViewSet, basename='study-group')
router.register(r'notifications', NotificationScheduleViewSet, basename='notification')

urlpatterns = router.urls


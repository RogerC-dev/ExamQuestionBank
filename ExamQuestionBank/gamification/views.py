from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Badge, UserBadge, UserXPLog, StudyGroup, StudyGroupMembership, NotificationSchedule
from .serializers import (
    BadgeSerializer,
    UserBadgeSerializer,
    UserXPLogSerializer,
    StudyGroupSerializer,
    StudyGroupMembershipSerializer,
    NotificationScheduleSerializer,
)
from .services import GamificationService, StudyGroupService


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).select_related('badge')


class UserXPViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = UserXPLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserXPLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def total(self, request):
        total = GamificationService.total_xp(request.user)
        return Response({'total_xp': total})


class StudyGroupViewSet(viewsets.ModelViewSet):
    serializer_class = StudyGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.select_related('owner')

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        StudyGroupService.add_member(group, self.request.user, role='moderator')

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        membership, created = StudyGroupService.add_member(group, request.user)
        serializer = StudyGroupMembershipSerializer(membership)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group = self.get_object()
        StudyGroupService.remove_member(group, request.user)
        return Response({'detail': '已退出學習小組'})


class NotificationScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


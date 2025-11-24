from rest_framework import serializers
from .models import Badge, UserBadge, UserXPLog, StudyGroup, StudyGroupMembership, NotificationSchedule


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = "__all__"


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["id", "badge", "awarded_at"]


class UserXPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserXPLog
        fields = ["id", "source", "delta", "metadata", "created_at"]


class StudyGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = StudyGroup
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "visibility",
            "max_members",
            "created_at",
            "updated_at",
            "members_count",
        ]
        read_only_fields = ["owner"]

    def get_members_count(self, obj):
        return obj.memberships.count()


class StudyGroupMembershipSerializer(serializers.ModelSerializer):
    group = StudyGroupSerializer(read_only=True)

    class Meta:
        model = StudyGroupMembership
        fields = ["id", "group", "role", "joined_at"]


class NotificationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSchedule
        fields = "__all__"
        read_only_fields = ["user", "sent_at", "created_at"]


from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Discussion, DiscussionVote, ContentReport
from .serializers import DiscussionSerializer, DiscussionVoteSerializer, ContentReportSerializer


class DiscussionViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Discussion.objects.select_related('user', 'question', 'parent')

    def get_queryset(self):
        queryset = self.queryset
        question_id = self.request.query_params.get('question')
        if question_id:
            queryset = queryset.filter(question_id=question_id, parent__isnull=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        parent = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, parent=parent, question=parent.question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        discussion = self.get_object()
        serializer = DiscussionVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data['vote_type']

        vote, created = DiscussionVote.objects.update_or_create(
            discussion=discussion,
            user=request.user,
            defaults={'vote_type': vote_type},
        )

        upvotes = DiscussionVote.objects.filter(discussion=discussion, vote_type='up').count()
        downvotes = DiscussionVote.objects.filter(discussion=discussion, vote_type='down').count()
        discussion.upvotes = upvotes
        discussion.downvotes = downvotes
        discussion.save(update_fields=['upvotes', 'downvotes'])

        return Response(self.get_serializer(discussion).data)

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        discussion = self.get_object()
        serializer = ContentReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ContentReport.objects.create(discussion=discussion, user=request.user, **serializer.validated_data)
        discussion.is_flagged = True
        discussion.save(update_fields=['is_flagged'])
        return Response({'detail': '已回報這則討論'}, status=status.HTTP_201_CREATED)

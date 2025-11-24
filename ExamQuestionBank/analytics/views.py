from rest_framework import permissions, viewsets

from .models import StudyMetric, Recommendation, MockExamPerformance
from .serializers import StudyMetricSerializer, RecommendationSerializer, MockExamPerformanceSerializer


class StudyMetricViewSet(viewsets.ModelViewSet):
    serializer_class = StudyMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudyMetric.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MockExamPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = MockExamPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MockExamPerformance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

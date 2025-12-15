from rest_framework import serializers
from .models import StudyMetric, Recommendation


class StudyMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMetric
        fields = '__all__'
        read_only_fields = ['user']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
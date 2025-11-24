from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Badge, StudyGroup

User = get_user_model()


class GamificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gamer', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.badge = Badge.objects.create(name='Starter', threshold=10)

    def test_list_badges(self):
        response = self.client.get('/api/v1/gamification/badges/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_create_study_group(self):
        payload = {'name': 'Group A', 'description': 'Test group'}
        response = self.client.post('/api/v1/study-groups/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudyGroup.objects.count(), 1)

    def test_join_study_group(self):
        owner = self.user
        group = StudyGroup.objects.create(name='Joinable', owner=owner)
        response = self.client.post(f'/api/v1/study-groups/{group.id}/join/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schedule_notification(self):
        payload = {
            'title': 'Reminder',
            'payload': {'type': 'study'},
            'scheduled_for': '2030-01-01T00:00:00Z',
        }
        response = self.client.post('/api/v1/notifications/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


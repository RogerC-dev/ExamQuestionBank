from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase

from question_bank.models import Question
from .models import Discussion, DiscussionVote, ContentReport

User = get_user_model()


class DiscussionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='discussion-user',
            email='discussion-user@example.com',
            password='pass1234'
        )
        self.question = Question.objects.create(
            subject='民法',
            category='測驗題',
            question_type='選擇題',
            difficulty='medium',
            status='published',
            content='討論測試題目',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_discussion(self):
        data = {'question': self.question.id, 'title': '測試討論', 'content': '這是一則討論內容'}
        response = self.client.post('/api/v1/discussions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discussion.objects.count(), 1)

    def test_reply_to_discussion(self):
        discussion = Discussion.objects.create(user=self.user, question=self.question, title='主題', content='內容')
        url = f'/api/v1/discussions/{discussion.id}/reply/'
        response = self.client.post(url, {'content': '回覆內容', 'title': 'Re'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(discussion.replies.count(), 1)

    def test_vote_discussion(self):
        discussion = Discussion.objects.create(user=self.user, question=self.question, title='主題', content='內容')
        vote_url = f'/api/v1/discussions/{discussion.id}/vote/'
        response = self.client.post(vote_url, {'vote_type': 'up'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        discussion.refresh_from_db()
        self.assertEqual(discussion.upvotes, 1)

    def test_report_discussion(self):
        discussion = Discussion.objects.create(user=self.user, question=self.question, title='主題', content='內容')
        report_url = f'/api/v1/discussions/{discussion.id}/report/'
        response = self.client.post(report_url, {'reason': '垃圾訊息'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ContentReport.objects.filter(discussion=discussion).exists())


class DiscussionPropertyTests(HypothesisTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='prop-disc',
            email='prop-disc@example.com',
            password='pass1234'
        )
        self.question = Question.objects.create(
            subject='刑法',
            category='測驗題',
            question_type='選擇題',
            difficulty='medium',
            status='published',
            content='property question',
        )
        self.client.force_authenticate(user=self.user)

    @settings(deadline=None, max_examples=25)
    @given(st.lists(st.sampled_from(['up', 'down']), min_size=1, max_size=10))
    def test_vote_aggregates_consistently(self, votes):
        discussion = Discussion.objects.create(user=self.user, question=self.question, title='prop', content='content')
        vote_url = f'/api/v1/discussions/{discussion.id}/vote/'
        for vote in votes:
            response = self.client.post(vote_url, {'vote_type': vote})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        discussion.refresh_from_db()
        expected_up = votes.count('up')
        expected_down = votes.count('down')
        self.assertEqual(discussion.upvotes, expected_up)
        self.assertEqual(discussion.downvotes, expected_down)

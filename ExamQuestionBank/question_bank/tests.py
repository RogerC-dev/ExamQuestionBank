from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from .models import Tag, Question


class BulkQuestionAPITest(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		# Create some tags
		self.tag1 = Tag.objects.create(name='contract')
		self.tag2 = Tag.objects.create(name='tort')

	def test_bulk_create_questions(self):
		payload = [
			{
				'subject': 'Civil Law',
				'category': 'contract',
				'question_type': '選擇題',
				'difficulty': 'easy',
				'status': 'draft',
				'content': 'This is the first test question',
				'explanation': 'Some explanation',
				'tag_ids': [self.tag1.id],
				'options': [
					{'content': 'A', 'is_correct': True},
					{'content': 'B', 'is_correct': False}
				]
			},
			{
				'subject': 'Civil Law',
				'category': 'tort',
				'question_type': '選擇題',
				'difficulty': 'medium',
				'status': 'published',
				'content': 'This is the second test question',
				'explanation': 'Some explanation 2',
				'tag_ids': [self.tag2.id],
				'options': [
					{'content': 'True', 'is_correct': True},
					{'content': 'False', 'is_correct': False}
				]
			}
		]

		url = '/api/v1/question_bank/questions/bulk-create/'
		response = self.client.post(url, data=payload, format='json')
		self.assertEqual(response.status_code, 200)
		results = response.data.get('results')
		self.assertTrue(isinstance(results, list))
		# Ensure both created
		self.assertEqual(len([r for r in results if r['success']]), 2)

	def test_bulk_update_questions(self):
		# create a sample question to update
		q = Question.objects.create(subject='Civil Law', category='contract', content='Original content', question_type='選擇題', difficulty='easy', status='draft', created_by=self.user)
		q.tags.set([self.tag1])

		payload = [
			{'id': q.id, 'content': 'Updated content', 'status': 'published', 'tag_ids': [self.tag2.id]}
		]

		url = '/api/v1/question_bank/questions/bulk-update/'
		response = self.client.patch(url, data=payload, format='json')
		self.assertEqual(response.status_code, 200)
		results = response.data.get('results')
		self.assertTrue(isinstance(results, list))
		self.assertEqual(len([r for r in results if r['success']]), 1)
		q.refresh_from_db()
		self.assertEqual(q.content, 'Updated content')
		self.assertEqual(q.status, 'published')
		self.assertTrue(self.tag2 in q.tags.all())

# Create your tests here.

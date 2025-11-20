import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from question_bank.models import AIChatHistory, Question
from question_bank.services.ai_service import AIService, ai_service

class AIServiceTest(TestCase):
    def setUp(self):
        self.service = AIService()

    @patch('question_bank.services.ai_service.OpenAI')
    def test_chat_success(self, mock_openai):
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="AI Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Re-initialize service to use mock
        service = AIService()
        service.api_key = "test_key"
        service.client = mock_client

        response = service.chat("Hello")
        self.assertEqual(response, "AI Response")
        mock_client.chat.completions.create.assert_called_once()

    def test_chat_no_api_key(self):
        # Ensure no API key
        self.service.api_key = None
        self.service.client = None
        
        response = self.service.chat("Hello")
        self.assertIn("尚未設定", response)

    @patch('question_bank.services.ai_service.OpenAI')
    def test_analyze_case_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        analysis_text = """
        摘要：這是一個測試案例。
        1. 關鍵點1
        2. 關鍵點2
        相關法條：刑法第100條
        """
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=analysis_text))]
        mock_client.chat.completions.create.return_value = mock_response

        service = AIService()
        service.api_key = "test_key"
        service.client = mock_client

        result = service.analyze_case("Case text")
        self.assertEqual(result['summary'].strip(), analysis_text.strip())
        self.assertIn("關鍵點1", result['key_points'])
        self.assertIn("刑法第100條", result['related_laws'])


class AIChatViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('ai_chat')

    @patch('question_bank.services.ai_service.ai_service.chat')
    def test_chat_endpoint_success(self, mock_chat):
        mock_chat.return_value = "AI Response"
        
        data = {'message': 'Hello'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], "AI Response")
        self.assertTrue(AIChatHistory.objects.filter(user=self.user).exists())

    def test_chat_endpoint_no_message(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('question_bank.services.ai_service.ai_service.chat')
    def test_usage_limit(self, mock_chat):
        mock_chat.return_value = "Response"
        
        # Create 10 history records
        for i in range(10):
            AIChatHistory.objects.create(
                user=self.user,
                message=f"msg {i}",
                response="resp"
            )
            
        data = {'message': 'Hello'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class AIAnalyzeCaseViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('ai_analyze_case')

    @patch('question_bank.services.ai_service.ai_service.analyze_case')
    def test_analyze_case_success(self, mock_analyze):
        mock_analyze.return_value = {
            "summary": "Summary",
            "key_points": ["Point 1"],
            "related_laws": ["Law 1"]
        }
        
        data = {'case_text': 'Case text'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary'], "Summary")
        self.assertTrue(AIChatHistory.objects.filter(user=self.user, context_type='case').exists())

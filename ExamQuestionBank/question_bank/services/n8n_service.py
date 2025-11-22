"""
N8N Integration Service
Provides async workflow automation for essay grading, batch processing, and scheduled tasks
"""
import os
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class N8NService:
    """N8N workflow automation service"""

    def __init__(self):
        self.webhook_url = os.getenv('N8N_WEBHOOK_URL', getattr(settings, 'N8N_WEBHOOK_URL', None))
        self.api_key = os.getenv('N8N_API_KEY', getattr(settings, 'N8N_API_KEY', None))
        self.enabled = bool(self.webhook_url)

    def is_configured(self) -> bool:
        """Check if N8N is configured"""
        return self.enabled

    def trigger_essay_grading(self, essay_submission_id: int) -> bool:
        """
        Trigger async essay grading workflow via N8N

        Args:
            essay_submission_id: Essay submission ID

        Returns:
            True if triggered successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("N8N not configured, skipping workflow trigger")
            return False

        try:
            payload = {
                'action': 'grade_essay',
                'essay_submission_id': essay_submission_id
            }

            response = requests.post(
                f"{self.webhook_url}/essay-grading",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else {},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Essay grading workflow triggered for submission {essay_submission_id}")
                return True
            else:
                logger.error(f"N8N webhook returned status {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error triggering N8N workflow: {str(e)}")
            return False

    def trigger_batch_recommendations(self, user_ids: list) -> bool:
        """
        Trigger batch recommendation generation for multiple users

        Args:
            user_ids: List of user IDs

        Returns:
            True if triggered successfully, False otherwise
        """
        if not self.is_configured():
            return False

        try:
            payload = {
                'action': 'batch_recommendations',
                'user_ids': user_ids
            }

            response = requests.post(
                f"{self.webhook_url}/batch-recommendations",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else {},
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Batch recommendations workflow triggered for {len(user_ids)} users")
                return True
            else:
                logger.error(f"N8N webhook returned status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error triggering batch recommendations: {str(e)}")
            return False

    def trigger_scheduled_analysis(self) -> bool:
        """
        Trigger scheduled progress analysis for all active users

        Returns:
            True if triggered successfully, False otherwise
        """
        if not self.is_configured():
            return False

        try:
            payload = {
                'action': 'scheduled_analysis'
            }

            response = requests.post(
                f"{self.webhook_url}/scheduled-analysis",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else {},
                timeout=60
            )

            if response.status_code == 200:
                logger.info("Scheduled analysis workflow triggered")
                return True
            else:
                logger.error(f"N8N webhook returned status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error triggering scheduled analysis: {str(e)}")
            return False

    def handle_webhook_callback(self, data: Dict[str, Any]) -> bool:
        """
        Handle callback from N8N workflow

        Args:
            data: Callback data from N8N

        Returns:
            True if handled successfully, False otherwise
        """
        try:
            action = data.get('action')
            result = data.get('result')

            if action == 'essay_grading_complete':
                essay_submission_id = data.get('essay_submission_id')
                # Process the grading result
                logger.info(f"Essay grading completed for submission {essay_submission_id}")
                # Here you would update the EssayGrading model with the result
                return True

            elif action == 'recommendations_generated':
                user_id = data.get('user_id')
                logger.info(f"Recommendations generated for user {user_id}")
                return True

            else:
                logger.warning(f"Unknown N8N callback action: {action}")
                return False

        except Exception as e:
            logger.error(f"Error handling N8N callback: {str(e)}")
            return False


# Create singleton instance
n8n_service = N8NService()




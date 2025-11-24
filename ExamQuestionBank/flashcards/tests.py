from datetime import date, timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate
from hypothesis import given, strategies as st, settings
from hypothesis import assume

from question_bank.models import Question
from .models import Flashcard
from .services import SpacedRepetitionService
from .views import FlashcardViewSet

User = get_user_model()


class FlashcardTestBase(TestCase):
	"""Shared helpers for property-based flashcard tests."""

	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(
			username='prop-user',
			email='prop-user@example.com',
			password='secret123'
		)

	def _create_question(self, subject='刑法') -> Question:
		return Question.objects.create(
			subject=subject,
			category='測驗題',
			question_type='選擇題',
			difficulty='medium',
			status='published',
			content=f'Property question {uuid4()}',
		)

	def _create_flashcard(self, **overrides) -> Flashcard:
		defaults = dict(
			user=self.user,
			question=self._create_question(),
			next_review_date=date.today(),
		)
		defaults.update(overrides)
		return Flashcard.objects.create(**defaults)


class SpacedRepetitionServiceTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='tester',
			email='tester@example.com',
			password='pass1234'
		)
		self.question = Question.objects.create(
			subject='民法',
			category='測驗題',
			question_type='選擇題',
			difficulty='medium',
			status='published',
			content='Sample question content',
		)
		self.flashcard = Flashcard.objects.create(
			user=self.user,
			question=self.question,
		)

	def test_spaced_repetition_progresses_interval_on_success(self):
		"""Higher ratings should expand intervals and move status forward."""
		first = SpacedRepetitionService.calculate_next_review(self.flashcard, rating=5)

		# Simulate saving outcome for the next review
		self.flashcard.interval = first.interval
		self.flashcard.repetition = first.repetition
		self.flashcard.ease_factor = first.ease_factor

		second = SpacedRepetitionService.calculate_next_review(self.flashcard, rating=5)

		self.assertGreaterEqual(second.interval, first.interval)
		self.assertGreaterEqual(second.ease_factor, first.ease_factor)
		self.assertIn(second.status, ['reviewing', 'mastered'])

	def test_failed_review_resets_progress(self):
		self.flashcard.interval = 10
		self.flashcard.repetition = 5
		outcome = SpacedRepetitionService.calculate_next_review(self.flashcard, rating=1)

		self.assertEqual(outcome.interval, 1)
		self.assertEqual(outcome.repetition, 0)
		self.assertEqual(outcome.status, 'learning')


class FlashcardDueFilterTests(TestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = User.objects.create_user(
			username='due-user',
			email='due-user@example.com',
			password='secret123'
		)
		self.question = Question.objects.create(
			subject='刑法',
			category='單選',
			question_type='選擇題',
			difficulty='easy',
			status='published',
			content='Another sample question',
		)

	def test_due_endpoint_only_returns_due_cards(self):
		due_card = Flashcard.objects.create(
			user=self.user,
			question=self.question,
			next_review_date=date.today(),
		)

		Flashcard.objects.create(
			user=self.user,
			question=Question.objects.create(
				subject='刑法',
				category='單選',
				question_type='選擇題',
				difficulty='easy',
				status='published',
				content='Future question',
			),
			next_review_date=date.today() + timedelta(days=3),
		)

		view = FlashcardViewSet.as_view({'get': 'due'})
		request = self.factory.get('/api/v1/flashcards/due/')
		force_authenticate(request, user=self.user)
		response = view(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['id'], due_card.id)


class SpacedRepetitionPropertyTests(FlashcardTestBase):
	@settings(deadline=None, max_examples=50)
	@given(
		interval=st.integers(min_value=1, max_value=90),
		repetition=st.integers(min_value=0, max_value=15),
		ease_factor=st.floats(min_value=1.3, max_value=3.0, allow_nan=False, allow_infinity=False),
		rating=st.integers(min_value=-5, max_value=10),
	)
	def test_sm2_outcome_respects_core_invariants(self, interval, repetition, ease_factor, rating):
		flashcard = Flashcard(
			user=self.user,
			question=self._create_question(),
			interval=interval,
			repetition=repetition,
			ease_factor=ease_factor,
		)

		outcome = SpacedRepetitionService.calculate_next_review(flashcard, rating)

		self.assertGreaterEqual(outcome.interval, 1)
		self.assertGreaterEqual(outcome.ease_factor, SpacedRepetitionService.MIN_EASE_FACTOR)
		self.assertGreaterEqual(outcome.repetition, 0)
		self.assertGreaterEqual((outcome.next_review_date - timezone.now().date()).days, 1)

		clamped_rating = max(SpacedRepetitionService.MIN_RATING, min(SpacedRepetitionService.MAX_RATING, rating))
		if clamped_rating < 3:
			self.assertEqual(outcome.repetition, 0)
			self.assertEqual(outcome.interval, 1)
		else:
			self.assertGreaterEqual(outcome.repetition, repetition if repetition else 0)
			self.assertIn(outcome.status, ['learning', 'reviewing', 'mastered'])


class FlashcardDuePropertyTests(FlashcardTestBase):
	@settings(deadline=None, max_examples=25)
	@given(
		offsets=st.lists(
			st.integers(min_value=-5, max_value=10),
			min_size=1,
			max_size=10,
		),
	)
	def test_due_endpoint_matches_manual_filter(self, offsets):
		Flashcard.objects.filter(user=self.user).delete()
		Question.objects.exclude(id__isnull=True)
		for offset in offsets:
			next_date = timezone.now().date() + timedelta(days=offset)
			self._create_flashcard(next_review_date=next_date)

		list_view = FlashcardViewSet.as_view({'get': 'list'})
		request = self.factory.get('/api/v1/flashcards/', {'status': 'due'})
		force_authenticate(request, user=self.user)
		response_filtered = list_view(request)

		due_view = FlashcardViewSet.as_view({'get': 'due'})
		due_request = self.factory.get('/api/v1/flashcards/due/')
		force_authenticate(due_request, user=self.user)
		response_due = due_view(due_request)

		due_ids = sorted(card['id'] for card in response_due.data)
		filtered_ids = sorted(card['id'] for card in response_filtered.data)
		self.assertEqual(filtered_ids, due_ids)

		manual_due_count = len([o for o in offsets if o <= 0])
		self.assertEqual(len(due_ids), manual_due_count)


class FlashcardStatsPropertyTests(FlashcardTestBase):
	@settings(deadline=None, max_examples=25)
	@given(
		offsets=st.lists(
			st.integers(min_value=-3, max_value=14),
			min_size=1,
			max_size=12,
		),
	)
	def test_stats_endpoint_reflects_queryset_counts(self, offsets):
		Flashcard.objects.filter(user=self.user).delete()
		for offset in offsets:
			next_date = timezone.now().date() + timedelta(days=offset)
			self._create_flashcard(next_review_date=next_date)

		stats_view = FlashcardViewSet.as_view({'get': 'stats'})
		request = self.factory.get('/api/v1/flashcards/stats/')
		force_authenticate(request, user=self.user)
		response = stats_view(request)

		self.assertEqual(response.status_code, 200)
		total_cards = len(offsets)
		due_cards = len([o for o in offsets if o <= 0])
		completion = 0 if total_cards == 0 else round(((total_cards - due_cards) / total_cards) * 100, 2)

		self.assertEqual(response.data['total_cards'], total_cards)
		self.assertEqual(response.data['due_cards'], due_cards)
		self.assertEqual(response.data['completion_percent'], completion)
		if offsets:
			expected_next = min(offsets)
			expected_date = timezone.now().date() + timedelta(days=expected_next)
			self.assertEqual(response.data['next_review_date'], expected_date)

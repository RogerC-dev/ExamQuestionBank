from dataclasses import dataclass
from datetime import date, timedelta
from django.utils import timezone


@dataclass
class ReviewOutcome:
    """Structured response describing the next review state."""

    ease_factor: float
    interval: int
    repetition: int
    next_review_date: date
    status: str


class SpacedRepetitionService:
    """Implements the SM-2 spaced repetition scheduling algorithm."""

    MIN_EASE_FACTOR = 1.3
    MAX_RATING = 5
    MIN_RATING = 1

    STATUS_THRESHOLDS = {
        'learning': 0,
        'reviewing': 3,
        'mastered': 8,
    }

    @classmethod
    def calculate_next_review(cls, flashcard, rating: int) -> ReviewOutcome:
        """Return updated parameters after applying SM-2 with given rating."""

        rating = max(cls.MIN_RATING, min(cls.MAX_RATING, int(rating)))
        ease_factor = flashcard.ease_factor or 2.5
        interval = max(1, flashcard.interval or 1)
        repetition = flashcard.repetition or 0

        if rating < 3:
            repetition = 0
            interval = 1
        else:
            if repetition == 0:
                interval = 1
            elif repetition == 1:
                interval = 6
            else:
                interval = round(interval * ease_factor)

            repetition += 1
            ease_delta = 0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)
            ease_factor = max(cls.MIN_EASE_FACTOR, round(ease_factor + ease_delta, 4))

        next_review_date = timezone.now().date() + timedelta(days=interval)
        status = cls._determine_status(repetition)

        return ReviewOutcome(
            ease_factor=ease_factor,
            interval=interval,
            repetition=repetition,
            next_review_date=next_review_date,
            status=status,
        )

    @classmethod
    def _determine_status(cls, repetition: int) -> str:
        if repetition >= cls.STATUS_THRESHOLDS['mastered']:
            return 'mastered'
        if repetition >= cls.STATUS_THRESHOLDS['reviewing']:
            return 'reviewing'
        return 'learning'

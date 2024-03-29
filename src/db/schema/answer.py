from enum import Enum
from random import choice, choices

from pydantic import BaseModel


class Sentiment(str, Enum):
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'
    POSITIVE = 'positive'


class Answer(BaseModel):
    text: str
    sentiment: Sentiment


class AnswerChoices:
    _PHRASES_NEGATIVE = [
        'nope',
        'nerp',
        'probably not',
        'not a chance',
        'not likely...',
        'ha!',
        'did hell freeze over?',
        'no',
        'you\'re kidding, right?',
    ]

    _PHRASES_NEUTRAL = [
        'meh',
        'maybe',
        'possibly',
        'not sure',
        'could go either way',
        'well, I guess anything is possible...',
    ]

    _PHRASES_POSITIVE = [
        'oh ya',
        'yep',
        'of course',
        'definitely',
        'ya!',
        'there\'s a good chance of it',
    ]

    _PHRASES_ANY = _PHRASES_NEGATIVE + _PHRASES_NEUTRAL + _PHRASES_POSITIVE

    ANSWERS_NEGATIVE = [Answer(text=text, sentiment=Sentiment.NEGATIVE) for text in _PHRASES_NEGATIVE]
    ANSWERS_NEUTRAL = [Answer(text=text, sentiment=Sentiment.NEUTRAL) for text in _PHRASES_NEUTRAL]
    ANSWERS_POSITIVE = [Answer(text=text, sentiment=Sentiment.POSITIVE) for text in _PHRASES_POSITIVE]
    ANSWERS_ANY = (
        [Answer(text=text, sentiment=Sentiment.NEGATIVE) for text in _PHRASES_NEGATIVE] +
        [Answer(text=text, sentiment=Sentiment.NEUTRAL) for text in _PHRASES_NEUTRAL] +
        [Answer(text=text, sentiment=Sentiment.POSITIVE) for text in _PHRASES_POSITIVE]
    )

    # TODO: Change this to take weights optional weights for negative, neutral and positive  sentiments
    @staticmethod
    def any():
        """ Returns a random answer with any sentiment. """
        return choice(AnswerChoices.ANSWERS_ANY)

    @staticmethod
    def negative():
        """ Always returns an answer with a negative sentiment. """
        return choice(AnswerChoices.ANSWERS_NEGATIVE)

    @staticmethod
    def neutral():
        """ Always returns an answer with a neutral sentiment. """
        return choice(AnswerChoices.ANSWERS_NEUTRAL)

    @staticmethod
    def positive():
        """ Always returns an answer with a positive sentiment. """
        return choice(AnswerChoices.ANSWERS_POSITIVE)

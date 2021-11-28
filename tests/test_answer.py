import pytest

from src.db.schema.answer import Answer, AnswerChoices, Sentiment


class TestAnswerChoices():

    @pytest.mark.parametrize('answer_callable', [
        AnswerChoices.any,
        AnswerChoices.negative,
        AnswerChoices.neutral,
        AnswerChoices.positive,
    ])
    def test_answer_returned(self, answer_callable):
        assert isinstance(answer_callable(), Answer)

    @pytest.mark.parametrize('answer_callable,sentiment', [
        (AnswerChoices.any, None),
        (AnswerChoices.negative, Sentiment.NEGATIVE),
        (AnswerChoices.neutral, Sentiment.NEUTRAL),
        (AnswerChoices.positive, Sentiment.POSITIVE),
    ])
    def test_answer_sentiment(self, answer_callable, sentiment):
        answer = answer_callable()
        assert isinstance(answer.sentiment, Sentiment)
        if sentiment:
            assert answer.sentiment == sentiment

    def test_negative(self):
        answer = AnswerChoices.negative()
        assert answer in AnswerChoices.ANSWERS_NEGATIVE
        assert answer.text in AnswerChoices._PHRASES_NEGATIVE

    def test_neutral(self):
        answer = AnswerChoices.neutral()
        assert answer in AnswerChoices.ANSWERS_NEUTRAL
        assert answer.text in AnswerChoices._PHRASES_NEUTRAL

    def test_positive(self):
        answer = AnswerChoices.positive()
        assert answer in AnswerChoices.ANSWERS_POSITIVE
        assert answer.text in AnswerChoices._PHRASES_POSITIVE

    def test_any(self):
        answer = AnswerChoices.any()
        assert answer in AnswerChoices.ANSWERS_ANY
        assert answer.text in AnswerChoices._PHRASES_ANY

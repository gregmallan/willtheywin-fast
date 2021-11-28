import pytest

from src.db.schema.answer import Answer, AnswerChoices


class TestAnswerChoices():

    @pytest.mark.parametrize('answer_callable', [
        AnswerChoices.any,
        AnswerChoices.negative,
        AnswerChoices.neutral,
        AnswerChoices.positive,
    ])
    def test_answer_returned(self, answer_callable):
        assert isinstance(answer_callable(), Answer)

    def test_negative(self):
        answer = AnswerChoices.negative()
        assert answer in AnswerChoices.ANSWERS_NEGATIVE

    def test_neutral(self):
        answer = AnswerChoices.neutral()
        assert answer in AnswerChoices.ANSWERS_NEUTRAL

    def test_positive(self):
        answer = AnswerChoices.positive()
        assert answer in AnswerChoices.ANSWERS_POSITIVE

    def test_any(self):
        answer = AnswerChoices.any()
        assert answer in AnswerChoices.ANSWERS_NEGATIVE + AnswerChoices.ANSWERS_NEUTRAL + AnswerChoices.ANSWERS_POSITIVE

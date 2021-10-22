from typing import Optional

from fastapi import FastAPI

from models.answer import Answer, AnswerChoices, Sentiment
from models.team import Team

app = FastAPI()


@app.get('/')
async def read_root():
    return {'msg': 'Will they win???'}


@app.get('/ask/{team}')
async def will_they_win(team: str, sentiment: Optional[Sentiment] = None):
    answer_choices_callable = AnswerChoices.any
    if sentiment == Sentiment.NEGATIVE:
        answer_choices_callable = AnswerChoices.negative
    elif sentiment == Sentiment.NEUTRAL:
        answer_choices_callable = AnswerChoices.neutral
    elif sentiment == Sentiment.POSITIVE:
        answer_choices_callable = AnswerChoices.positive

    answer = answer_choices_callable()
    return {'team': team, 'answer': answer, 'requested_sentiment': sentiment}


@app.post('/team/create')
async def create_team(team: Team):
    return {'team': team, 'status': 'OK'}

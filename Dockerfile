FROM tiangolo/uvicorn-gunicorn:python3.9

COPY conf/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# These are setup as volumes
#COPY ./src /willtheywin-fast/src/
#COPY ./migrations /willtheywin-fast/migrations
#COPY ./tests /willtheywin-fast/tests/

COPY ./alembic.ini /willtheywin-fast/alembic.ini
COPY ./conftest.py /willtheywin-fast/conftest.py
COPY ./pytest.ini /willtheywin-fast/pytest.ini

WORKDIR /willtheywin-fast

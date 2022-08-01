FROM tiangolo/uvicorn-gunicorn:python3.9

COPY conf/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# These are setup as volumes
#COPY ./src /willtheywin-fast/src/
#COPY ./migrations /willtheywin-fast/migrations
#COPY ./tests /willtheywin-fast/tests/

COPY ./seedall.py /willtheywin-fast/seedall.py

COPY ./alembic.ini /willtheywin-fast/alembic.ini
COPY ./conftest.py /willtheywin-fast/conftest.py
COPY ./pytest.ini /willtheywin-fast/pytest.ini

COPY ./scripts /willtheywin-fast/scripts/

WORKDIR /willtheywin-fast

ENV USER apiuser
ENV HOME /home/$USER

RUN useradd -m $USER && echo $USER:$USER | chpasswd && adduser $USER sudo
#RUN chown $USER:$USER $HOME
RUN chown -R $USER:$USER /willtheywin-fast

USER $USER

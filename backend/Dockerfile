FROM python:3.7-slim
# ...
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc

COPY ./requirements.txt /requirements.txt
COPY ./app.yml /app.yml
COPY ./ /backend
WORKDIR /backend

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home django-user

ENV PATH="/py/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

USER django-user

# Gunicorn as app server
CMD exec daphne -b 0.0.0.0 -p 8080 backend.asgi:application
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=messenger.settings

WORKDIR /app

RUN apt-get update && apt-get install -y gcc

RUN apt-get update && apt-get install -y wait-for-it

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

ENV DJANGO_ENV=local

CMD ["gunicorn", "messenger.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=dmoneytracker.settings.production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

ARG BRANCH=main
RUN git clone --depth=1 --branch ${BRANCH} \
    https://github.com/hiteshmohite19/d-money-tracker.git .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p logs static staticfiles && \
    SECRET_KEY=build-only-dummy-key python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "dmoneytracker.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

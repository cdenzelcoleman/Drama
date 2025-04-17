FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for Alpine
RUN apk update && apk add --no-cache \
    build-base \
    cargo \
    jpeg-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    zlib-dev && \
    apk upgrade --no-cache

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "drama.wsgi:application", "--bind", "0.0.0.0:8000"]
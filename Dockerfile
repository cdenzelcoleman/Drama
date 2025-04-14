FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies with cache optimization
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the code
COPY . /app/

# Collect static files and expose port 8000
RUN python manage.py collectstatic --noinput
EXPOSE 8000

# Command to run your application with Gunicorn
CMD ["gunicorn", "drama.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

# Create logs dir and use a non-root user
RUN adduser --disabled-password --gecos "" appuser \ 
    && mkdir -p /app/logs         && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Security-conscious default: don't log plaintext passwords
ENV LOG_PASSWORDS=false
ENV LOG_DIR=/app/logs

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]

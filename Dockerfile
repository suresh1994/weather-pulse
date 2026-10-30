FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

EXPOSE 8000

# On startup: fetch fresh data, then serve
CMD ["sh", "-c", "python app/fetch_weather.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
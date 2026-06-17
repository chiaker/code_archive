FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so they are cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (dataset/ can also be bind-mounted at run time).
COPY app/ ./app/
COPY dataset/ ./dataset/

EXPOSE 8000

# Index whatever .py files are in dataset/ on startup, then serve the API.
# Indexing into a fresh DB each start keeps the container stateless.
CMD ["sh", "-c", "python -m app.indexer dataset/ && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

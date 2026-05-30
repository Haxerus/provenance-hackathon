FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY reference_lib ./reference_lib
COPY registry ./registry
COPY private_keys ./private_keys
COPY backend ./backend
ENV PROVENANCE_ROOT=/app
EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

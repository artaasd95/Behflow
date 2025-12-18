FROM python:3.11-slim

WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-db.txt ./

# Install dependencies
RUN pip install -r requirements.txt -r requirements-db.txt

# Copy application code
COPY . .

# Copy shared module
COPY ../shared /app/shared

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

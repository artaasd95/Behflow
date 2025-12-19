FROM python:3.11-slim

WORKDIR /app

# Copy requirements files
COPY requirements.txt ../behflow_agent/requirements.txt ./

# Install dependencies (including agent requirements)
RUN pip install -r requirements.txt -r ../behflow_agent/requirements.txt

# Copy application code
COPY . .

# Copy agent package into image so imports succeed
COPY ../behflow_agent /app/behflow_agent

# Copy shared module
COPY ../shared /app/shared

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

WORKDIR /app

# Copy requirements file (paths are relative to the build context, which is ../src)
COPY backend/requirements.txt ./requirements.txt

# Install dependencies
# Note: we intentionally install only the backend requirements to avoid pin conflicts
# with the separate `behflow_agent/requirements.txt`. If a missing requirement is discovered
# later, I'll ask you to add it to `backend/requirements.txt`.
RUN pip install -r requirements.txt

# Copy application code
COPY backend/ /app

# Copy agent package into image so imports succeed
COPY behflow_agent /app/behflow_agent

# Copy shared module
COPY shared /app/shared

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

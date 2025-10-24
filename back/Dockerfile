FROM python:3.13-slim AS base

RUN apt update && apt install -y build-essential libpq-dev python3-dev cron
RUN mkdir -p /var/log/cron

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY back/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY back/ .

COPY --from=dcp-frontend-builder /app/out /app/public
# Expose port 8000 for the application
EXPOSE 8000

WORKDIR /app/app
# Start the FastAPI application using Uvicorn
CMD ["/app/entrypoint.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


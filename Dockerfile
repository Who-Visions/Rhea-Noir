# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Cloud Run defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Run the server
# Use shell form to allow variable expansion if needed, but array form is safer for signals.
# We explicitly bind to 0.0.0.0 and the PORT env var.
CMD ["sh", "-c", "uvicorn rhea_server:app --host 0.0.0.0 --port ${PORT}"]

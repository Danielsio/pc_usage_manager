# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ADMIN_USER admin
ENV ADMIN_EMAIL ""
ENV ADMIN_PASSWORD ""

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Add entrypoint script
COPY entrypoint.sh /app/
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

# Expose port 8000
EXPOSE 8000

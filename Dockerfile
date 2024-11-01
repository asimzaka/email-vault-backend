# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container

COPY . /app
# Expose the port the app will run on
EXPOSE 5000

# Define the environment variable for Flask to run
ENV FLASK_APP=flask/main.py
ENV FLASK_ENV=development

# Run the Flask application
CMD ["python", "flask/main.py"]

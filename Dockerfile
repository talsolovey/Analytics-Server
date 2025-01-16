# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

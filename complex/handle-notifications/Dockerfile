# Use an official Python runtime as a parent image
FROM python:3-slim

# Set the working directory in the container
ENV PYTHONUNBUFFERED=1

# Set the timezone to GMT+8
ENV TZ=Asia/Singapore

WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .


# Run your application
CMD ["python", "./app.py"]
# Use an official Python runtime as a parent image
FROM python:3-slim

# Set the timezone to GMT+8
ENV TZ=Asia/Singapore

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run your application
CMD ["python", "./app.py"]
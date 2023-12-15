# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /backend

# Install the required system packages for building MySQL client
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the project code to the working directory
COPY . .

# Set the DJANGO_ENV environment variable
ARG DJANGO_ENV
ENV DJANGO_ENV=${DJANGO_ENV}

# Expose the port on which the Django server will run
EXPOSE 8000

# Run the Django server
RUN python manage.py makemigrations accounts 

# Run Gunicorn
CMD gunicorn accounts.wsgi:application --bind 0.0.0.0:8000
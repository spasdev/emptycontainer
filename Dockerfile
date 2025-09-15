# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file and install them
# This is done in a separate step to leverage Docker's build cache
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the command to run the application using Gunicorn
# This command uses the PORT environment variable provided by Cloud Run
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "main:app"]

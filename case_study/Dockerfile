FROM python:3.11

WORKDIR /case_study

# Copy only the requirements.txt to the working directory
COPY requirements.txt .

# Install dependencies
RUN apt-get update && \
  apt-get install -y gcc python3-dev libev-dev

ENV CASS_DRIVER_NO_CYTHON=1

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["flask", "run"]

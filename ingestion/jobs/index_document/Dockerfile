FROM python:3.9


ENV PYFLINK_VERSION=1.18
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies including JDK 11
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk gcc g++ curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run the consumer
CMD ["python", "main.py"]


FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports if needed
EXPOSE 5672 9092

# Run the script
CMD ["python", "main.py"]

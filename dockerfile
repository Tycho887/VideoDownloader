# Use the official Python image
FROM python:3.10.12-slim

# Set the working directory
WORKDIR /app

# Copy the bot code and requirements
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "main.py"]

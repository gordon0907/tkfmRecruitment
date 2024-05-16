# Use the official Python 3 image
FROM python:3

# Set environment variable for the bot token
ENV TELEGRAM_BOT_TOKEN=

# Set the working directory in the container
WORKDIR /app

# Copy all files from the current directory to the container
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir easyocr playwright python-telegram-bot

# Install the required browsers and system dependencies for Playwright
RUN playwright install
RUN playwright install-deps

# Create a volume for persistent data
VOLUME ["/app/data"]

# Run the main Python script
ENTRYPOINT ["python", "main.py"]

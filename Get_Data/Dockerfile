FROM python:3.9

# Set the working directory
WORKDIR /app

# Install dependencies from requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scraper files
COPY . /app/

# Run the scraper
CMD ["python", "main.py"]

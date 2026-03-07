FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*
CMD ["python", "main.py", "run", "--interface", "all"]

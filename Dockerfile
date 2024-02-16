FROM python:3.10-slim as worker
WORKDIR /workspace
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY app.py func.py /workspace/
EXPOSE 10651
CMD ["python", "/workspace/app.py"]

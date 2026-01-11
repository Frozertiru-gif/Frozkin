FROM python:3.12-slim
WORKDIR /app
COPY apps/uploader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/uploader/uploader.py ./uploader.py
CMD ["python", "uploader.py"]

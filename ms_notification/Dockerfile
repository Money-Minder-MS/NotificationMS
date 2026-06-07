FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .. .
EXPOSE 8086
CMD daphne -b 0.0.0.0 -p 8086 ms_notification.asgi:application
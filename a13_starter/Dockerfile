FROM python:3.11-slim

WORKDIR /app

COPY a13_starter/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY a13_starter /app/a13_starter

EXPOSE 8000

CMD ["python", "-m", "a13_starter.api_server"]

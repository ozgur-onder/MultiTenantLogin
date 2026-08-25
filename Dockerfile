FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn psycopg2-binary python-multipart jinja2

EXPOSE 5000

CMD ["uvicorn", "sunucu:app", "--host", "0.0.0.0", "--port", "5000"]
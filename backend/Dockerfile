FROM python:3.12-alpine

RUN pip install --no-cache-dir "psycopg[binary]==3.2.*"

WORKDIR /app
COPY app.py .

EXPOSE 8000
CMD ["python", "app.py"]

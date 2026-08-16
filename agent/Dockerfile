FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent/app ./app
COPY knowledge-base /knowledge-base

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

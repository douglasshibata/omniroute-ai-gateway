FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PORT=20128
ENV HOST=0.0.0.0
EXPOSE 20128

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "20128"]

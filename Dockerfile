FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV DATA_DIR=/opt/infraops

EXPOSE 8080

CMD ["python", "app.py"]
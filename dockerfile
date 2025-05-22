# Python imajı
FROM python:3.11-slim

# Ortam değişkenleri
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Sistem paketlerini yükle
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Gereken dosyaları kopyala
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Port
EXPOSE 8000

# Uygulama komutu (production için gunicorn)
CMD ["gunicorn", "llm.wsgi:application", "--bind", "0.0.0.0:8000"]

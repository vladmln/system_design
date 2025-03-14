# Стадия сборки
FROM python:3.10-slim as builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Стадия финального образа
FROM python:3.10-slim

WORKDIR /app

# Копирование только необходимых файлов
COPY --from=builder /root/.local /root/.local
COPY . .

# Настройка переменных окружения
ENV PATH=/root/.local/bin:$PATH

# Запуск сервиса
CMD ["sh", "-c", "if [ \"$SERVICE\" = \"user\" ]; then python user_service.py; else python wall_service.py; fi"]
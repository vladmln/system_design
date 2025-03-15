FROM python:3.10-slim as builder

WORKDIR /app

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

CMD ["sh", "-c", "if [ \"$SERVICE\" = \"user\" ]; then python user_service.py; elif [ \"$SERVICE\" = \"wall\" ]; then python wall_service.py; else python message_service.py; fi"]
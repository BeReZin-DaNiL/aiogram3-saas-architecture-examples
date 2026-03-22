FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Принудительно запускаем миграции перед стартом бота
CMD alembic upgrade head && python run_bot.py
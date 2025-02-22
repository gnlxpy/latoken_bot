# Используем официальный образ Python 3.13
FROM python:3.13.2-slim

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY . .

# Устанавливаем переменные окружения
ENV OPENAI_TOKEN=""
ENV TG_TOKEN=""
ENV REDIS_PSW=""
ENV TOKENIZERS_PARALLELISM="false"


# Запускаем приложение
CMD ["python", "tg_bot.py"]
FROM python:3.11.7

ENV PYTHONUNBUFFERED=1

# Обновляем пакеты и устанавливаем зависимости
RUN apt-get update && apt-get install -y curl

# Добавляем NodeSource APT репозиторий для установки Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -

# Устанавливаем Node.js
RUN apt-get install -y nodejs

# Проверка установки Node.js и npm
RUN node -v && npm -v

# Копируем файл с зависимостями Python
COPY ./requirements.txt /requirements.txt

# Устанавливаем Python-зависимости
RUN pip install -r /requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем файлы бота
COPY ./bot /bot/

# Запускаем бота
CMD ["python", "/bot/main.py"]
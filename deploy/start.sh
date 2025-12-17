#!/bin/bash


sleep 1

echo "Применение миграций..."
alembic upgrade head

echo "Запуск приложения..."
python src/core/root/main.py

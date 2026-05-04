#!/bin/bash
# scripts/init_db.sh

echo "🚀 Запускаем PostgreSQL в Docker..."
docker-compose up -d postgres

echo "⏳ Ожидаем готовности PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U postgres -d grilnica; do
  sleep 2
done

echo "✅ PostgreSQL готов!"

echo "📦 Применяем миграции Alembic..."
alembic upgrade head

echo "🎉 База данных готова к работе!"
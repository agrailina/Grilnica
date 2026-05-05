1. ПОДНИМИ БД
docker-compose up -d db     

2. МИГРАЦИИ СДЕЛАЙ
docker exec -it market-app-1 alembic upgrade head

3. ПОДНИМИ СЕРВИС
docker-compose build --no-cache app        

4. ЗАПУСТИ СКРИПТ ДОБАВЛЕНИЯ ДАННЫХ
docker exec -it market-app-1 python scripts/seed_combo.py

5. ЕСЛИ ХОЧЕШЬ ОЧИСТИ БАЗУ 
docker exec -it market-app-1 python scripts/clear_db.py --mode products
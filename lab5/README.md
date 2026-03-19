# Biology Testing System

## Запуск

```bash
# 1. Поднять все контейнеры одной командой
docker-compose up --build

# 2. Открыть в браузере:
#   Frontend:  http://localhost:3000
#   Swagger:   http://localhost:8000/docs
#   Health:    http://localhost:8000/health
```

## Остановка

```bash
docker-compose down          # остановить
docker-compose down -v       # остановить + удалить данные БД
```

## Проверка работы

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs backend
docker-compose logs db
docker-compose logs frontend
```
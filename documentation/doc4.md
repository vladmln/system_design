# Лабораторная работа 4: Гибридная СУБД (PostgreSQL + MongoDB)

## Структура проекта
app/
├── docker-compose.yml
├── Dockerfile
├── user_service.py # PostgreSQL + JWT
├── wall_service.py # PostgreSQL
├── message_service.py # MongoDB
├── init_postgres.sql
├── init_mongo.js
└── requirements.txt

Задание четвертой лабораторной работы
1. Создайте сервис на Python который реализует сервисы, спроектированные в первом задании (по проектированию). Должно быть реализовано как минимум два сервиса (управления пользователем, и хотя бы один «бизнес» сервис)
2. Сервис должен поддерживать аутентификацию с использованием JWT-token
3. Сервис должен реализовывать как минимум GET/POST методы
4. Данные сервиса должны храниться в памяти
5. В целях проверки должен быть заведён мастер-пользователь (имя admin, пароль secret)

Дополнение третьей ЛР:
6. Данные должны храниться в СУБД PostgreSQL;
7. Должны быть созданы таблицы для каждой сущности из вашего задания;
8. Должен быть создан скрипт по созданию базы данных и таблиц, а также наполнению СУБД тестовыми значениями;
9. Для сущности, должны быть созданы запросы к БД (CRUD) согласно ранее разработанной архитектуре
10. Данные о пользователе должны включать логин и пароль. Пароль должен храниться в закрытом виде (хэширован) – в этом задании опционально
11. Должно применяться индексирования по полям, по которым будет производиться поиск

Дополнение четвертой ЛР:
12. Одна из сущностей должна храниться в mongoDB;
13. Сервис должен осуществлять создание и чтение нужного документа из mongoDB;
14. Должны быть построены индексы соответственно критерию запроса; Работа должны содержать docker-compose.yml, который:
- запускает приложение app в контейнере (собирается из dockerfile), которое выполняет вариант задания
- запускает базу данных PostgreSQL и mongoDB в отдельных контейнере
- проводит первоначальную инициализацию баз данных

# Руководство по использованию сервиса

## 1. Установка зависимостей
```powershell
pip install -r requirements.txt

## 2. Запуск системы
docker compose down -v --remove-orphans  # Очистка
docker compose build --no-cache         # Сборка
docker compose up                      # Запуск

## 3. Регистрация пользователя
curl -Method POST -Uri "http://localhost:5000/register" `
-ContentType "application/json" `
-Body '{"username": "user1", "password": "pass1"}'

### Ответ:
{"message":"User created"}

## 4. Авторизация
$token = (curl -Method POST -Uri "http://localhost:5000/login" `
-ContentType "application/json" `
-Body '{"username": "user1", "password": "pass1"}').Content | ConvertFrom-Json | Select-Object -ExpandProperty access_token

### Ответ:
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
## 5. Работа со стеной (PostgreSQL)
## Добавление поста
curl -Method POST -Uri "http://localhost:5001/wall/user1" `
-Headers @{"Authorization"="Bearer $token"} `
-ContentType "application/json" `
-Body '{"text": "Hello PostgreSQL!"}'

### Ответ:
{"message":"Post added","post_id":1}

### Просмотр постов
curl -Method GET -Uri "http://localhost:5001/wall/user1" `
-Headers @{"Authorization"="Bearer $token"}

### Ответ:
{
  "username": "user1",
  "posts": [
    {
      "id": 1,
      "text": "Hello PostgreSQL!",
      "created_at": "2025-03-14T22:00:00.123Z"
    }
  ]
}

## 6. Работа с сообщениями (MongoDB)
### Отправка сообщения
curl -Method POST -Uri "http://localhost:5002/messages/user1" `
-Headers @{"Authorization"="Bearer $token"} `
-ContentType "application/json" `
-Body '{"text": "Hello MongoDB!"}'

### Ответ:
{"message":"Message sent","message_id":"65f3c8d4e4b0e0c8d4e4b0e0"}

### Просмотр сообщений
curl -Method GET -Uri "http://localhost:5002/messages/user1" `
-Headers @{"Authorization"="Bearer $token"}

### Ответ:
{
  "username": "user1",
  "messages": [
    {
      "id": "65f3c8d4e4b0e0c8d4e4b0e0",
      "text": "Hello MongoDB!",
      "created_at": "2025-03-14T22:00:00.123Z"
    }
  ]
}

## 7. Проверка данных в БД
### PostgreSQL
docker exec -it app-postgres-1 psql -U user -d social -c "SELECT * FROM users;"
docker exec -it app-postgres-1 psql -U user -d social -c "SELECT * FROM posts;"

### MongoDB
docker exec -it app-mongo-1 mongosh social --eval "db.users.find().pretty()"
docker exec -it app-mongo-1 mongosh social --eval "db.messages.find().pretty()"

## 8. Остановка системы
docker compose down -v




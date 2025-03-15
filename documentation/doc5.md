# Лабораторная работа 5: Гибридная СУБД + Redis

Задание пятой лабораторной работы
1. Создайте сервис на Python который реализует сервисы, спроектированные в первом задании (по проектированию). Должно быть реализовано как минимум два сервиса (управления пользователем, и хотя бы один «бизнес» сервис)
2. Сервис должен поддерживать аутентификацию с использованием JWT-token
3. Сервис должен реализовывать как минимум GET/POST методы
4. Данные сервиса должны храниться в памяти
5. В целях проверки должен быть заведён мастер-пользователь (имя admin, пароль secret)
6. Данные должны храниться в СУБД PostgreSQL;
7. Должны быть созданы таблицы для каждой сущности из вашего задания;
8. Должен быть создан скрипт по созданию базы данных и таблиц, а также наполнению СУБД тестовыми значениями;
9. Для сущности, должны быть созданы запросы к БД (CRUD) согласно ранее разработанной архитектуре
10. Данные о пользователе должны включать логин и пароль. Пароль должен храниться в закрытом виде (хэширован) – в этом задании опционально
11. Должно применяться индексирования по полям, по которым будет производиться поиск
12. Одна из сущностей должна храниться в mongoDB;
13. Сервис должен осуществлять создание и чтение нужного документа из mongoDB;
14. Должны быть построены индексы соответственно критерию запроса;
15. Одна из сущностей, которая хранится в PostgreSQL должна кешироваться в Redis
16. Реализовать паттерн «сквозное чтение» для работы с Redis

## Руководство по использованию сервиса
### 1. Регистрация пользователя
curl -Method POST -Uri "http://localhost:5000/register" `
-ContentType "application/json" `
-Body '{"username": "user1", "password": "pass1"}'

### 2. Авторизация
$token = (curl -Method POST -Uri "http://localhost:5000/login" `
-ContentType "application/json" `
-Body '{"username": "user1", "password": "pass1"}').Content | ConvertFrom-Json | Select-Object -ExpandProperty access_token

### Ответ :
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

### 3. Проверка кеша в Redis
docker exec -it app-redis-1 redis-cli KEYS "user:*"
docker exec -it app-redis-1 redis-cli GET "user:user1"

### Ответ
"user:user1"
"{\"id\": 2, \"username\": \"user1\", \"password_hash\": \"$2b$12$QRcVz9JWEY9J0fAZXJ4uCu0cpTRsr3X6rhhKhE4oDgSDTw9QtZd/m\", \"is_admin\": false}"

### 4. Работа с постами
### Добавление поста
curl -Method POST -Uri "http://localhost:5001/wall/user1" `
-Headers @{"Authorization"="Bearer $token"} `
-ContentType "application/json" `
-Body '{"text": "Hello PostgreSQL!"}'

### Просмотр постов
curl -Method GET -Uri "http://localhost:5001/wall/user1" `
-Headers @{"Authorization"="Bearer $token"}

### Ответ :
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

### 5. Работа с сообщениями
### Отправка сообщения
curl -Method POST -Uri "http://localhost:5002/messages/user1" `
-Headers @{"Authorization"="Bearer $token"} `
-ContentType "application/json" `
-Body '{"text": "Hello MongoDB!"}'

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
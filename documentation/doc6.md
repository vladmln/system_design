# Лабораторная работа 6: Гибридная СУБД + CQRS + Kafka

## Задание шестой лабораторной работы
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
17. Реализовать паттерн CQRS для одной из сущностей
18. Метод POST должен публиковать сообщение о создании в очередь kafka, отдельный сервис должен читать сообщения и записывать их в базу

## Варианты использования
### 1. Регистрация и авторизация
```powershell
# Регистрация
curl -Method POST -Uri "http://localhost:5000/register" `
-ContentType "application/json" `
-Body '{"username": "user1", "password": "pass1"}'

# Авторизация
$token = (curl -Method POST -Uri "http://localhost:5000/login" `
-ContentType "application/json" `
-Body '{"username": "user1", "password": "pass1"}').Content | ConvertFrom-Json | Select-Object -ExpandProperty access_token

# Добавление поста через Kafka
curl -Method POST -Uri "http://localhost:5001/wall/user1" `
-Headers @{"Authorization"="Bearer $token"} `
-ContentType "application/json" `
-Body '{"text": "Kafka Post"}'

# Проверка записи в PostgreSQL
docker exec -it app-postgres-1 psql -U user -d social -c "SELECT * FROM posts;"

# Проверка логов Kafka Consumer
docker compose logs cqrs-consumer

# Отправка сообщения
curl -Method POST -Uri "http://localhost:5002/messages/user1" `
-Headers @{"Authorization"="Bearer $token"} `
-ContentType "application/json" `
-Body '{"text": "MongoDB Message"}'

# Просмотр сообщений
curl -Method GET -Uri "http://localhost:5002/messages/user1" `
-Headers @{"Authorization"="Bearer $token"}

# Проверка кеша пользователя
docker exec -it app-redis-1 redis-cli GET "user:user1"

# Просмотр всех ключей кеша
docker exec -it app-redis-1 redis-cli KEYS "user:*"
workspace {
  model {
    user = person "Пользователь" "Внешний пользователь системы"

    system = softwareSystem "Социальная сеть" "Гибридная система с CQRS, Kafka и Redis" {
      user_service = container "User Service" "Регистрация/авторизация + Redis-кеш" "Flask 3.0.3, SQLAlchemy, Bcrypt, JWT, Redis 7.0"
      wall_service = container "Wall Service" "CQRS: Запись постов через Kafka" "Flask 3.0.3, Kafka 7.6.1"
      message_service = container "Message Service" "Управление сообщениями (MongoDB)" "Flask 3.0.3, PyMongo, JWT"
      cqrs_consumer = container "CQRS Consumer" "Асинхронная запись постов в PostgreSQL" "Python 3.10, Kafka 7.6.1, SQLAlchemy"
      postgres = container "PostgreSQL" "Хранение пользователей/постов" "PostgreSQL 13"
      mongo = container "MongoDB" "Хранение сообщений" "MongoDB 6.0"
      redis = container "Redis" "Кеширование пользователей" "Redis 7.0"
      kafka = container "Kafka" "Событийная шина" "Apache Kafka 7.6.1"
      zookeeper = container "Zookeeper" "Координация Kafka" "Apache Zookeeper 7.6.1"
    }

    user -> user_service "Регистрация/Авторизация (HTTP/JSON)"
    user -> wall_service "POST /wall (HTTP/JSON + JWT)"
    user -> message_service "POST/GET /messages (HTTP/JSON + JWT)"
    
    user_service -> postgres "SQL-запросы (SELECT/INSERT)"
    user_service -> redis "Кеширование пользователей (GET/SET)"
    
    wall_service -> kafka "Публикация событий post_created"
    cqrs_consumer -> kafka "Чтение событий post_created"
    cqrs_consumer -> postgres "INSERT в таблицу posts"
    
    message_service -> mongo "NoSQL-операции (INSERT/SELECT)"
  }

  views {
    systemContext system {
      include *
      autoLayout
      description "Контекстная диаграмма системы"
    }

    container system {
      include *
      autoLayout
      description "Диаграмма контейнеров"
    }

    dynamic system {
      title "CQRS Процесс записи поста"
      description "Асинхронная обработка через Kafka"
      wall_service -> kafka "Отправка post_created event" "Kafka Producer"
      kafka -> cqrs_consumer "Обработка события" "Kafka Consumer"
      cqrs_consumer -> postgres "Запись в таблицу posts" "SQL INSERT"
    }

    dynamic system {
      title "Авторизация с Redis"
      description "Сквозное чтение пользователей"
      user -> user_service "POST /login" "JSON"
      user_service -> redis "Проверка кеша" "GET user:{username}"
      user_service -> postgres "Если нет в кеше" "SQL SELECT"
      user_service -> redis "Сохранение в кеш" "SET user:{username}"
    }
  }
}
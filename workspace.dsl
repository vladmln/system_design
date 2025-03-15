workspace {
  model {
    user = person "Пользователь" "Внешний пользователь системы"

    system = softwareSystem "Социальная сеть" "Гибридная система с PostgreSQL и MongoDB" {
      user_service = container "User Service" "Регистрация и авторизация (Flask + PostgreSQL)" "Flask 3.1.3, SQLAlchemy, Bcrypt, JWT"
      wall_service = container "Wall Service" "Управление постами (Flask + PostgreSQL)" "Flask 3.1.3, SQLAlchemy, JWT"
      message_service = container "Message Service" "Управление сообщениями (Flask + MongoDB)" "Flask 3.1.3, PyMongo, JWT"
      postgres = container "PostgreSQL" "Хранение пользователей и постов" "PostgreSQL 13"
      mongo = container "MongoDB" "Хранение сообщений" "MongoDB 6.0"
    }

    user -> user_service "Регистрация/Авторизация (HTTP/JSON)"
    user -> wall_service "Управление постами (HTTP/JSON + JWT)"
    user -> message_service "Отправка сообщений (HTTP/JSON + JWT)"
    
    user_service -> postgres "Чтение/запись данных (SQL)"
    wall_service -> postgres "Чтение/запись данных (SQL)"
    message_service -> mongo "Чтение/запись данных (NoSQL)"
    
    Rel(user_service, wall_service, "Проверка токена", "JWT")
    Rel(user_service, message_service, "Проверка токена", "JWT")
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
      title "Процесс авторизации"
      description "Пользователь получает JWT-токен"
      user -> user_service "POST /login" "JSON"
      user_service -> postgres "SELECT * FROM users" "SQL"
      user_service -> user "200 OK (JWT)" "JSON"
    }
  }
}
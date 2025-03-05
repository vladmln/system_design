workspace {
    model {
        // Акторы системы
        customer = person "Regular User" "Зарегистрированный пользователь соцсети"
        guest = person "Guest User" "Незарегистрированный посетитель"

        // Основная система
        social_network = softwareSystem "Social Network" "Социальная сеть с базовыми функциями" {
            // Контейнеры приложения
            web_client = container "Web Client" "Веб-интерфейс на React" "React + TypeScript"
            mobile_client = container "Mobile Client" "Мобильное приложение" "React Native"
            
            api_gateway = container "API Gateway" "Точка входа и аутентификация" "Spring Cloud Gateway"
            user_service = container "User Service" "Управление учетными записями" "Spring Boot"
            wall_service = container "Wall Service" "Операции со стенами" "Go"
            chat_service = container "Chat Service" "Обмен сообщениями" "Socket.IO + Node.js"
            media_service = container "Media Service" "Хранение медиа" "Python (FastAPI)"
            
            primary_db = container "Primary DB" "Основная БД пользователей и постов" "PostgreSQL"
            chat_db = container "Chat DB" "Хранение сообщений" "MongoDB"
            cache = container "Cache" "Кэширование сессий" "Redis"
        }

        // Внешние системы
        cdn = softwareSystem "CDN" "Доставка статики" "AWS CloudFront"
        email_service = softwareSystem "Email Service" "Отправка писем" "Amazon SES"

        // Связи
        customer -> web_client
        customer -> mobile_client
        guest -> web_client
        
        web_client -> api_gateway "REST over HTTPS"
        mobile_client -> api_gateway "GraphQL over HTTPS"
        
        api_gateway -> user_service "gRPC"
        api_gateway -> wall_service "gRPC"
        api_gateway -> chat_service "WebSocket"
        
        user_service -> primary_db "JDBC"
        user_service -> cache "Redis"
        user_service -> email_service "SMTP"
        
        wall_service -> primary_db "PostgreSQL"
        wall_service -> media_service "REST"
        
        chat_service -> chat_db "MongoDB"
        chat_service -> cache "Redis Pub/Sub"
        
        media_service -> cdn "S3 API"
    }

    views {
        // Контекстная диаграмма
        context social_network {
            include *
            autoLayout
            description "Взаимодействие с внешними системами"
        }
        
        // Контейнерная диаграмма
        container social_network {
            include *
            exclude cdn, email_service
            autoLayout tb
            description "Внутренняя архитектура"
        }
        
        // Динамическая диаграмма: отправка сообщения
        dynamic social_network {
            title "Отправка личного сообщения"
            description "Обработка сообщения между пользователями"
            
            customer -> web_client : Отправляет сообщение
            web_client -> api_gateway : Передает через WebSocket
            api_gateway -> chat_service : Маршрутизация
            chat_service -> chat_db : Сохраняет в MongoDB
            chat_service -> cache : Проверяет блокировки
            chat_service -> customer : Уведомляет получателя
        }
        
        // Диаграмма деплоя (Production)
        deployment social_network "Production" {
            group "AWS" {
                node "EC2 Cluster" {
                    containerInstance api_gateway
                    containerInstance user_service
                    containerInstance wall_service
                }
                
                node "Database Server" {
                    containerInstance primary_db
                    containerInstance chat_db
                }
                
                node "Cache Cluster" {
                    containerInstance cache
                }
            }
            
            node "CDN" {
                containerInstance cdn
            }
        }
    }
}
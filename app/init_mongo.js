// Создаем коллекции и индексы
db.createCollection('users');
db.users.createIndex({ username: 1 }, { unique: true });
db.createCollection('messages');
db.messages.createIndex({ user_id: 1 });
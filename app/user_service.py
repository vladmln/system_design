import redis
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt
import os
import time
from pymongo import MongoClient
from datetime import datetime
import json

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

# Подключение к PostgreSQL
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
time.sleep(10)  # Задержка для PostgreSQL
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=os.getenv('REDIS_PORT', 6379),
    decode_responses=True
)

# Подключение к MongoDB
mongo = MongoClient(
    host=os.getenv('MONGO_HOST', 'mongo'),
    port=27017,
    username='',
    password='',
    authSource='admin'
)
db = mongo.social
mongo_users = db.users

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)

# Паттерн "сквозное чтение"
def get_user_with_cache(username):
    cached_user = redis_client.get(f"user:{username}")
    if cached_user:
        return json.loads(cached_user)
    
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            user_data = {
                'id': user.id,
                'username': user.username,
                'password_hash': user.password_hash,  # ← Добавлено хэширование пароля
                'is_admin': user.is_admin
            }
            redis_client.set(f"user:{username}", json.dumps(user_data), ex=3600)
        return user_data if user else None
    finally:
        session.close()

Base.metadata.create_all(engine)

@app.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'error': 'Missing JSON in request'}), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    session = Session()
    try:
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'User exists'}), 400
        
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        new_user = User(username=username, password_hash=hashed.decode())
        session.add(new_user)
        session.commit()
        
        # Добавление в MongoDB
        mongo_user = {
            '_id': new_user.id,
            'username': username,
            'created_at': datetime.utcnow()
        }
        mongo_users.insert_one(mongo_user)
        
        return jsonify({'message': 'User created'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Registration error: {str(e)}'}), 500
    finally:
        session.close()

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:  # ← Проверка Content-Type
        return jsonify({'error': 'Missing JSON in request'}), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user_data = get_user_with_cache(username)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    if bcrypt.checkpw(password.encode(), user_data['password_hash'].encode()):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Invalid password'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
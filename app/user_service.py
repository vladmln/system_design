from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt
import os
import time
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

time.sleep(10)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)

Base.metadata.create_all(engine)

# Подключение к MongoDB
mongo = MongoClient(
    host=os.getenv('MONGO_HOST', 'mongo'),
    port=27017,
    username='',
    password='',
    authSource='admin'
)
db = mongo.social
mongo_users = db.users  # Коллекция для пользователей

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password').encode()
    
    session = Session()
    try:
        # Регистрация в PostgreSQL
        if session.query(User).filter_by(username=username).first():
            return jsonify({'error': 'User exists'}), 400
        
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        new_user = User(username=username, password_hash=hashed.decode())
        session.add(new_user)
        session.commit()
        
        # Добавление в MongoDB
        try:
            mongo_user = {
                '_id': new_user.id,
                'username': username,
                'created_at': datetime.utcnow()
            }
            mongo_users.insert_one(mongo_user)
        except Exception as mongo_e:
            print(f"MongoDB warning: {mongo_e}")  # ← Логируем, но не прерываем регистрацию
        
        return jsonify({'message': 'User created'}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Registration error: {str(e)}'}), 500
    finally:
        session.close()

    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password').encode()
    
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if bcrypt.checkpw(password, user.password_hash.encode()):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
        else:
            return jsonify({'error': 'Invalid password'}), 401
    except Exception as e:
        return jsonify({'error': f'Login error: {str(e)}'}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
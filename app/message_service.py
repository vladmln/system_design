from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

# Подключение к MongoDB
mongo = MongoClient(
    host=os.getenv('MONGO_HOST', 'mongo'),
    port=27017,
    username='',
    password='',
    authSource='admin'
)
db = mongo.social
messages = db.messages

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
Session = sessionmaker(bind=engine)

@app.route('/messages/<username>', methods=['POST'])
@jwt_required()
def send_message(username):
    try:
        data = request.get_json()
        text = data.get('text')
        
        # Получаем user_id из PostgreSQL
        with Session() as session:
            user = session.execute(
                text(f"SELECT id FROM users WHERE username='{username}'")
            ).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            user_id = user.id
        
        message = {
            'user_id': user_id,
            'text': text,
            'created_at': datetime.utcnow()
        }
        
        result = messages.insert_one(message)
        return jsonify({'message': 'Message sent', 'message_id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': f'MongoDB error: {str(e)}'}), 500

@app.route('/messages/<username>', methods=['GET'])
@jwt_required()
def get_messages(username):
    try:
        # Получаем user_id из PostgreSQL
        with Session() as session:
            user = session.execute(
                text(f"SELECT id FROM users WHERE username='{username}'")
            ).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            user_id = user.id
        
        user_messages = messages.find({'user_id': user_id}).sort('created_at', -1)
        formatted = [{
            'id': str(m['_id']),
            'text': m['text'],
            'created_at': m['created_at'].isoformat()
        } for m in user_messages]
        
        return jsonify({'username': username, 'messages': formatted})
    except Exception as e:
        return jsonify({'error': f'MongoDB error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
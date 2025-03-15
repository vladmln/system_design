from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from kafka import KafkaProducer
import json
from datetime import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5
)

# Подключение к PostgreSQL
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
Session = sessionmaker(bind=engine)

@app.route('/wall/<username>', methods=['POST'])
@jwt_required()
def add_post(username):
    try:
        data = request.get_json()
        text_content = data.get('text')
        
        session = Session()
        user = session.execute(
            text(f"SELECT id FROM users WHERE username='{username}'")
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        event = {
            'type': 'post_created',
            'user_id': user.id,
            'text': text_content,
            'created_at': datetime.utcnow().isoformat()
        }
        producer.send('post_events', event).get(timeout=10)  # ← Добавьте подтверждение
        return jsonify({'message': 'Post event sent'}), 202
    except Exception as e:
        return jsonify({'error': f'Kafka error: {str(e)}'}), 500
    finally:
        session.close()

@app.route('/wall/<username>', methods=['GET'])
@jwt_required()
def get_wall(username):
    try:
        session = Session()
        user = session.execute(
            text(f"SELECT id FROM users WHERE username = '{username}'")
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Получаем посты через raw SQL
        posts = session.execute(
            text(f"SELECT text, created_at FROM posts WHERE user_id = {user.id} ORDER BY created_at DESC")
        ).fetchall()
        
        formatted_posts = [{
            'text': p.text,
            'created_at': p.created_at.isoformat()
        } for p in posts]
        
        return jsonify({'username': username, 'posts': formatted_posts})
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
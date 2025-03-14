from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from sqlalchemy import create_engine, Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key')

# Подключение к БД
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default='now()')

Base.metadata.create_all(engine)

@app.route('/wall/<username>', methods=['POST'])
@jwt_required()
def add_post(username):
    data = request.get_json()
    text = data.get('text')
    
    session = Session()
    user = session.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    new_post = Post(user_id=user.id, text=text)
    session.add(new_post)
    session.commit()
    return jsonify({'message': 'Post added', 'post_id': new_post.id}), 201

@app.route('/wall/<username>', methods=['GET'])
@jwt_required()
def get_wall(username):
    session = Session()
    user = session.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    posts = session.query(Post).filter_by(user_id=user.id).all()
    formatted_posts = [{
        'id': p.id,
        'text': p.text,
        'created_at': p.created_at.isoformat()
    } for p in posts]
    
    return jsonify({'username': username, 'posts': formatted_posts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
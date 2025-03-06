from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 's3cr3t_k3y'
jwt = JWTManager(app)

# Хранилище постов в памяти
posts = {}

@app.route('/wall/<username>', methods=['GET'])
@jwt_required()
def get_wall(username):
    user_posts = posts.get(username, [])
    return jsonify({
        'username': username,
        'posts': user_posts
    })

@app.route('/wall/<username>', methods=['POST'])
@jwt_required()
def add_post(username):
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    current_user = get_jwt_identity()
    timestamp = datetime.utcnow().isoformat()
    
    post = {
        'author': current_user,
        'text': text,
        'timestamp': timestamp
    }
    
    if username not in posts:
        posts[username] = []
    posts[username].append(post)
    
    return jsonify({'message': 'Post added', 'post_id': len(posts[username])-1}), 201

if __name__ == '__main__':
    app.run(port=5001)
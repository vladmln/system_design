from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 's3cr3t_k3y'
jwt = JWTManager(app)

# Хранилище пользователей в памяти
users = {
    'admin': {
        'password_hash': generate_password_hash('secret'),
        'is_admin': True
    }
}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users:
        return jsonify({'error': 'User already exists'}), 400
    
    users[username] = {
        'password_hash': generate_password_hash(password),
        'is_admin': False
    }
    return jsonify({'message': 'User created'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = users.get(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/user/<username>', methods=['GET'])
@jwt_required()
def get_user(username):
    current_user = get_jwt_identity()
    user = users.get(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if current_user != username and not users[current_user].get('is_admin', False):
        return jsonify({'error': 'Forbidden'}), 403
    
    return jsonify({'username': username, 'is_admin': user['is_admin']})

if __name__ == '__main__':
    app.run(port=5000)
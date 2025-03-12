from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta  
from views.user_vm import UserView

auth_ctr = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_ctr.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    result, status = UserView.register_user(username, password_hash)
    return jsonify(result), status

@auth_ctr.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    user, status = UserView.get_user_by_username(username)

    if status != 200 or not bcrypt.check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Invalid username or password."}), 401

    access_token = create_access_token(identity=username)
    duration_minutes = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds() / 60)
    expiration_time = datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']

    return jsonify({
        "access_token": access_token,
        "expires_at": expiration_time.strftime('%Y-%m-%d %H:%M:%S') + ' UTC',
        "duration_minutes": duration_minutes
    }), 200

@auth_ctr.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as": current_user}), 200

@auth_ctr.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    users, status = UserView.get_all_users()
    return jsonify(users), status
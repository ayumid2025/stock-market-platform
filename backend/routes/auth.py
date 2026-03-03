from flask import Blueprint, request, jsonify
from models import db, User, Account
from auth import hash_password, check_password, generate_token, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'message': 'Missing fields'}), 400
    
    # Check if user exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'message': 'User already exists'}), 409
    
    hashed = hash_password(password)
    user = User(username=username, email=email, password_hash=hashed)
    db.session.add(user)
    db.session.flush()   # get user.id
    
    # Create account with default cash
    account = Account(user_id=user.id, cash_balance=10000.0)
    db.session.add(account)
    db.session.commit()
    
    token = generate_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'username': username, 'email': email}}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Missing fields'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = generate_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email}}), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile():
    user = User.query.get(request.user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    })

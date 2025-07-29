from flask import Blueprint, jsonify, request
from models import User, db
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON payload'}), 400

    username = data.get('username')
    email = data.get('email')

    if not isinstance(username, str) or not username.strip():
        return jsonify({'error': 'username must be a non-empty string'}), 400
    if not isinstance(email, str) or not email.strip():
        return jsonify({'error': 'email must be a non-empty string'}), 400

    try:
        user = User(username=username.strip(), email=email.strip())
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A user with this username or email already exists'}), 409 # Conflict

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    if not data:
        return jsonify({'error': 'Request body cannot be empty'}), 400

    try:
        if 'username' in data:
            new_username = data.get('username')
            if not isinstance(new_username, str) or not new_username.strip():
                return jsonify({'error': 'username must be a non-empty string'}), 400
            user.username = new_username.strip()
        
        if 'email' in data:
            new_email = data.get('email')
            if not isinstance(new_email, str) or not new_email.strip():
                return jsonify({'error': 'email must be a non-empty string'}), 400
            user.email = new_email.strip()

        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A user with this username or email already exists'}), 409 # Conflict

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

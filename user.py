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
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'error': 'username and email are required fields'}), 400

    # Check for non-empty strings
    if not isinstance(data['username'], str) or not data['username'].strip():
        return jsonify({'error': 'username must be a non-empty string'}), 400
    if not isinstance(data['email'], str) or not data['email'].strip():
        return jsonify({'error': 'email must be a non-empty string'}), 400

    try:
        user = User(username=data['username'].strip(), email=data['email'].strip())
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
        user.username = data.get('username', user.username).strip()
        user.email = data.get('email', user.email).strip()
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

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models import User, Role
from datetime import datetime, timedelta
import jwt
import os

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Get user role
        role = Role.query.get(user.role_id)
        if not role:
            return jsonify({'success': False, 'error': 'User role not found'}), 500
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': role.name,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': role.name,
                'role_id': user.role_id,
                'device_id': user.device_id or f'device_{user.id}'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Update user logout time
            user = User.query.get(user_id)
            if user:
                user.last_logout = datetime.utcnow()
                db.session.commit()
            
            return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify JWT token and return user info"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            role = Role.query.get(user.role_id)
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': role.name if role else None,
                    'role_id': user.role_id,
                    'device_id': user.device_id or f'device_{user.id}'
                }
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 
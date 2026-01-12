import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.user import User
from app import db

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Handle multipart/form-data for file uploads
    if 'avatar' in request.files:
        data = request.form
        file = request.files['avatar']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{user_id}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Delete old avatar if it exists and is a local file
            if user.avatar_url and not user.avatar_url.startswith('http'):
                old_avatar_path = os.path.join(current_app.root_path, 'static', user.avatar_url.lstrip('/'))
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            # Ensure the URL path includes the static folder prefix
            user.avatar_url = f'/static/avatars/{filename}'
    else:
        # Handle regular JSON data
        data = request.get_json()
        if 'avatar_url' in data:
          user.avatar_url = data.get('avatar_url')

    # Update other profile fields from 'data' which is either form or json
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.age = data.get('age', user.age)
    if data.get('age') == '': user.age = None # Handle empty string for age
    user.gender = data.get('gender', user.gender)
    user.bio = data.get('bio', user.bio)
    user.phone = data.get('phone', user.phone)
    user.location = data.get('location', user.location)

    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@profile_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_public_profile(user_id):
    """Get public profile of any user"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict_public()}), 200

@profile_bp.route('/profile/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500
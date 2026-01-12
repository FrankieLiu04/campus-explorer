from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import socketio
from flask_socketio import join_room, leave_room, emit
from app.models.user import User
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# 存储在线用户和消息历史
online_users = {}
message_history = []

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    # 移除断开连接的用户
    for username, sid in list(online_users.items()):
        if sid == request.sid:
            del online_users[username]
            emit('user_left', {
                'username': username,
                'online_users': len(online_users)
            }, broadcast=True)
            
            # 添加系统消息
            message_history.append({
                'type': 'system',
                'username': 'System',
                'content': f'{username} has left the chat',
                'timestamp': datetime.now().isoformat()
            })
            
            # 限制消息历史数量
            if len(message_history) > 50:
                message_history.pop(0)
            
            emit('online_users', len(online_users), broadcast=True)
            break

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    if username:
        online_users[username] = request.sid
        join_room('chat_room')
        
        # 发送当前在线用户数
        emit('online_users', len(online_users))
        
        # 发送加入消息给所有用户
        emit('user_joined', {
            'username': username,
            'online_users': len(online_users)
        }, broadcast=True)
        
        # 添加系统消息到历史
        message_history.append({
            'type': 'system',
            'username': 'System',
            'content': f'{username} has joined the chat',
            'timestamp': datetime.now().isoformat()
        })
        
        # 限制消息历史数量
        if len(message_history) > 50:
            message_history.pop(0)
        
        # 发送历史消息给新用户
        emit('previous_messages', message_history)
        
        print(f'{username} joined the chat. Online users: {len(online_users)}')

@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    content = data.get('content')
    timestamp = data.get('timestamp')
    msg_type = data.get('type', 'text')
    avatar_url = data.get('avatar_url')
    
    if username and content:
        message_data = {
            'type': msg_type,
            'username': username,
            'content': content,
            'timestamp': timestamp,
            'avatar_url': avatar_url
        }
        
        # 添加到消息历史
        message_history.append(message_data)
        
        # 限制消息历史数量
        if len(message_history) > 50:
            message_history.pop(0)
        
        # 广播消息给所有用户
        emit('message', message_data, broadcast=True)
        
        print(f'Message from {username}: {content}')
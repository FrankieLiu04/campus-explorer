from flask import Blueprint, request, current_app
from app import socketio, db
from flask_socketio import join_room, emit
from datetime import datetime
from app.models.chat_message import ChatMessage

chat_bp = Blueprint('chat', __name__)

# 存储在线用户和消息历史
online_users = {}

@socketio.on('connect')
def handle_connect():
    current_app.logger.info("socket_connected", extra={"sid": request.sid})

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
            system_msg = ChatMessage(
                msg_type="system",
                username="System",
                content=f"{username} has left the chat",
            )
            db.session.add(system_msg)
            db.session.commit()
            
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
        system_msg = ChatMessage(
            msg_type="system",
            username="System",
            content=f"{username} has joined the chat",
        )
        db.session.add(system_msg)
        db.session.commit()
        
        # 发送历史消息给新用户
        recent = (
            ChatMessage.query.order_by(ChatMessage.id.desc()).limit(50).all()
        )
        emit('previous_messages', [m.to_dict() for m in reversed(recent)])

        current_app.logger.info("user_joined_chat", extra={"username": username, "online_users": len(online_users)})

@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    content = data.get('content')
    msg_type = data.get('type', 'text')
    avatar_url = data.get('avatar_url')
    
    if username and content:
        msg = ChatMessage(
            msg_type=msg_type,
            username=username,
            content=content,
            avatar_url=avatar_url,
            timestamp=datetime.now(),
        )
        db.session.add(msg)
        db.session.commit()
        message_data = msg.to_dict()
        
        # 广播消息给所有用户
        emit('message', message_data, broadcast=True)
        current_app.logger.info("chat_message", extra={"username": username, "type": msg_type})

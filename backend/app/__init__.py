from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    
    from app.routes.auth import auth_bp
    from app.routes.map import map_bp
    from app.routes.chat import chat_bp
    from app.routes.profile import profile_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(map_bp, url_prefix='/api/map')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    
    return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import load_config
from app.observability import register_observability

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(load_config(instance_path=app.instance_path))

    if app.config.get("TRUST_PROXY_HEADERS"):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    logging.basicConfig(level=logging.INFO)

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config["SOCKETIO_CORS_ORIGINS"])

    register_observability(app)
    
    from app.routes.auth import auth_bp
    from app.routes.map import map_bp
    from app.routes.chat import chat_bp
    from app.routes.profile import profile_bp
    from app.routes.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(map_bp, url_prefix='/api/map')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(health_bp)
    
    return app

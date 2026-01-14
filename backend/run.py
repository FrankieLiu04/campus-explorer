from app import create_app, socketio, db
import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    socketio.run(app, debug=bool(app.config.get("DEBUG")), host=host, port=port)

from app import db


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg_type = db.Column(db.String(20), nullable=False, default="text")
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    avatar_url = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    def to_dict(self):
        return {
            "type": self.msg_type,
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "avatar_url": self.avatar_url,
        }


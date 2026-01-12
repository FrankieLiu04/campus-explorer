from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Extended profile fields
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'gender': self.gender,
            'bio': self.bio,
            'phone': self.phone,
            'location': self.location,
            'avatar_url': self.avatar_url,
        }

    def to_dict_public(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
        }
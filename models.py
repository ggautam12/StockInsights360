from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UsersInfo(db.Model):
    __tablename__ = 'users_info'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(50), nullable=False)

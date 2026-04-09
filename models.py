from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    invitation = db.relationship('Invitation', backref='owner', uselist=False)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True)
    
    # Data Mempelai
    bride_name = db.Column(db.String(100))
    groom_name = db.Column(db.String(100))
    bride_parents = db.Column(db.String(200)) # Baru
    groom_parents = db.Column(db.String(200)) # Baru
    
    # Waktu & Lokasi
    wedding_date = db.Column(db.String(50))
    wedding_time = db.Column(db.String(20))
    location_name = db.Column(db.String(200))
    maps_url = db.Column(db.String(500))
    
    # Tema & Visual
    theme_name = db.Column(db.String(50), default='luxury')
    hero_img = db.Column(db.String(500))    # Foto Welcome/BG
    couple_img = db.Column(db.String(500))  # Foto Berdua Utama
    groom_img = db.Column(db.String(500))   # Foto Pria
    bride_img = db.Column(db.String(500))   # Foto Wanita
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
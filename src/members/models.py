from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

DB_PATH = '/Users/drivera53/Development/master/Applications_of_Software_Architecture_for_Big_Data/dolphin_data_collector/instance/IgDolphin.sqlite3'

db = SQLAlchemy()

'''
Define the database model
that is used to store 
the IG data.
'''

class IgUsers(db.Model):
    __tablename__ = "ig_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False) # As per IG Api
    full_name = db.Column(db.String(60), unique=True, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.now())

    # A user can have MANY posts
    posts = db.relationship('IgPosts', back_populates='user', lazy='dynamic')

class IgPosts(db.Model):
    __tablename__ = "ig_posts"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(60), nullable=True)
    product_type = db.Column(db.String(60), nullable=True)
    caption = db.Column(db.String(2200), nullable=True)
    likes_count = db.Column(db.Integer, default=0)
    video_view_count = db.Column(db.Integer, default=0)
    video_play_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.now())

    # A post has ONLY ONE user
    user_id = db.Column(db.Integer, db.ForeignKey('ig_users.id'), unique=False, nullable=False)
    user = db.relationship("IgUsers", back_populates="posts") 
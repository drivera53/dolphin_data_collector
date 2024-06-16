#!/usr/bin/env python3
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil import parser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Weather.sqlite3'

'''
Define the database model
that is used to store 
the IG data.
'''

db = SQLAlchemy(app)

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

'''
Helper function to get updated post data from all IG accounts on file
using APIFY API
'''
def get_all_ig_posts():
    response = requests.get("https://api.apify.com/v2/acts/apify~instagram-api-scraper/runs/last/dataset/items?token=apify_api_TIHSy6bFZs94pmPGFdxjzOb3koxrVz03ZEag")
    return response.json()

def process_ig_posts(ig_posts_json):
    for curr_post in ig_posts_json:
        new_user = IgUsers(id=curr_post["ownerId"], username=curr_post["ownerUsername"], full_name=curr_post["ownerFullName"])
        insert_update_user(new_user)
        if (curr_post["type"] == "Video"):
            new_post = IgPosts(id=curr_post["id"], type=curr_post["type"], product_type=curr_post["productType"], caption=curr_post["caption"], likes_count=curr_post["likesCount"], video_view_count=curr_post["videoViewCount"], video_play_count=curr_post["videoPlayCount"], comments_count=curr_post["commentsCount"], timestamp=parser.parse(curr_post["timestamp"]), user_id=curr_post["ownerId"])
        else:
            new_post = IgPosts(id=curr_post["id"], type=curr_post["type"], caption=curr_post["caption"], likes_count=curr_post["likesCount"], comments_count=curr_post["commentsCount"], timestamp=parser.parse(curr_post["timestamp"]), user_id=curr_post["ownerId"])
        insert_update_post(new_post)

def insert_update_user(user):
    existing_user = db.session.get(IgUsers, user.id)
    if existing_user:
        existing_user.username = user.username
        existing_user.full_name = user.full_name
        existing_user.last_updated = default=datetime.now()
    else:
        db.session.add(user)
    db.session.commit()

def insert_update_post(post):
    existing_post = db.session.get(IgPosts, post.id)
    if existing_post:
        existing_post.caption = post.caption
        existing_post.likes_count = post.likes_count
        existing_post.video_view_count = post.video_view_count
        existing_post.video_play_count = post.video_play_count
        existing_post.comments_count = post.comments_count
        existing_post.last_updated = default=datetime.now()
    else:
        db.session.add(post)
    db.session.commit()

'''
In main we first get the current temperature and then 
create a new object that we can add to the database. 
'''
if __name__ == "__main__":
    ig_posts_json = get_all_ig_posts()
    with app.app_context():
        # db.drop_all() # Only on dev!
        db.create_all()
        process_ig_posts(ig_posts_json)
        # all_ig_users = IgUsers.query.all()
        # for ig_user in all_ig_users:
        #     print(f"username = {ig_user.username}, id = {ig_user.id}, full_name = {ig_user.full_name}, last_updated = {ig_user.last_updated}\n")
        # all_ig_posts = IgPosts.query.all()
        # for ig_post in all_ig_posts:
        #     print(f"id = {ig_post.id}, type = {ig_post.type}, product_type = {ig_post.product_type}, caption = {ig_post.caption}, likes_count = {ig_post.likes_count}, video_view_count = {ig_post.video_view_count}, video_play_count = {ig_post.video_play_count}, comments_count = {ig_post.comments_count}, timestamp = {ig_post.timestamp}, last_updated = {ig_post.last_updated}, user_id = {ig_post.user_id}\n")
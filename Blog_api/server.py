import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------- MODELS ------------------
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data.get('name', '')
        self.username = user_data.get('username', '')

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return User(user) if user else None

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[\W_]', password)
    )

# ----------------- AUTH ROUTES ------------------
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'msg': 'Email already exists'}), 400
    if not is_strong_password(data['password']):
        return jsonify({'msg': 'Weak password. Use upper, lower, digit, and special char'}), 400

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user_id = mongo.db.users.insert_one({
        'email': data['email'],
        'password': hashed_pw,
        'name': data.get('name', ''),
        'username': data.get('username', ''),
        'following': [],
        'confirmed': False
    }).inserted_id
    login_user(User(mongo.db.users.find_one({'_id': user_id})))
    return jsonify({'msg': 'User registered successfully'})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({'email': data['email']})
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        login_user(User(user))
        return jsonify({'msg': 'Login successful'})
    return jsonify({'msg': 'Invalid credentials'}), 401

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'msg': 'Logged out'})

# ----------------- FOLLOW ------------------
@app.route('/follow/<user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$addToSet': {'following': user_id}}
    )
    return jsonify({'msg': 'Followed user'})

# ----------------- POST ROUTES ------------------
@app.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.form
    image = request.files.get('image')
    image_url = ''

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'msg': 'Title and content are required'}), 400


    if image:
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result.get('secure_url', '')

    post = {
        'title': data['title'],
        'content': data['content'],
        'image': image_url,
        'author_id': current_user.id,
        'likes': [],
        'created_at': datetime.utcnow()
    }
    result = mongo.db.posts.insert_one(post)
    return jsonify({'msg': 'Post created', 'id': str(result.inserted_id)})

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = list(mongo.db.posts.find().sort('created_at', -1))
    for post in posts:
        post['_id'] = str(post['_id'])
        post['author_id'] = str(post['author_id'])
    return jsonify(posts)

@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'msg': 'Post not found'}), 404
    post['_id'] = str(post['_id'])
    post['author_id'] = str(post['author_id'])
    return jsonify(post)

@app.route('/posts/<post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    result = mongo.db.posts.delete_one({
        '_id': ObjectId(post_id),
        'author_id': current_user.id
    })
    if result.deleted_count:
        return jsonify({'msg': 'Post deleted'})
    return jsonify({'msg': 'Unauthorized or post not found'}), 403

# ----------------- FEED ------------------
@app.route('/feed', methods=['GET'])
@login_required
def get_feed():
    user = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    following_ids = user.get('following', [])
    posts = list(mongo.db.posts.find({'author_id': {'$in': following_ids}}).sort('created_at', -1))
    for post in posts:
        post['_id'] = str(post['_id'])
        post['author_id'] = str(post['author_id'])
    return jsonify(posts)

# ----------------- COMMENTS ------------------
@app.route('/comments/<post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    data = request.json
    comment = {
        'post_id': post_id,
        'user_id': current_user.id,
        'content': data['content'],
        'created_at': datetime.utcnow()
    }
    mongo.db.comments.insert_one(comment)
    return jsonify({'msg': 'Comment added'})

@app.route('/comments/<post_id>', methods=['GET'])
def get_comments(post_id):
    comments = list(mongo.db.comments.find({'post_id': post_id}))
    for c in comments:
        c['_id'] = str(c['_id'])
        c['user_id'] = str(c['user_id'])
    return jsonify(comments)

# ----------------- LIKES ------------------
@app.route('/likes/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'msg': 'Post not found'}), 404

    if current_user.id in post.get('likes', []):
        mongo.db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$pull': {'likes': current_user.id}}
        )
        return jsonify({'msg': 'Post unliked'})
    else:
        mongo.db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$addToSet': {'likes': current_user.id}}
        )
        return jsonify({'msg': 'Post liked'})

# ----------------- RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)

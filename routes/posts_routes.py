from flask import Blueprint, render_template, abort, request, jsonify
from bson import ObjectId
from jinja2 import TemplateNotFound
from pymongo import MongoClient
from datetime import datetime, timezone
from routes.auth_routes import verify_token

posts_bp = Blueprint('posts', __name__, template_folder = 'templates')

client = MongoClient('localhost', 27017)
from database import db 

CATEGORIES = {
    "meal": {
        "label": "식사",
        "class": "text-bg-danger"
    },
    "study": {
        "label": "공부",
        "class": "text-bg-success"
    }
}

FILTER_CATEGORIES = {
    "all": {
        "label": "전체",
        "class": "text-bg-warning"
    },
    "study": CATEGORIES["study"],
    "meal": CATEGORIES["meal"],
    "joined": {
        "label": "참여 중",
        "class": "text-bg-primary"
    }
}

@posts_bp.route('/')
def get_posts():
  user_payload = verify_token()
  user_id = user_payload['user_id'] if user_payload else None
  
  selected_category = request.args.get('category', 'all')

  if selected_category == 'all':
    posts = list(db.posts.find({}).sort('created_at', -1))
  else:
    posts = list(db.posts.find({'category': selected_category}).sort('created_at', -1))

  return render_template('posts.html', posts=posts, current_category=selected_category, categories=CATEGORIES, filter_categories=FILTER_CATEGORIES)

@posts_bp.route('/', methods=['POST'])
def post_meeting():
  title_receive = request.form['title']
  date_receive = request.form['date']
  time_receive = request.form['time']
  max_count_receive = request.form['max_count']
  content_receive = request.form['content']
  category_receive = request.form['category']

  new_post = {
        'title': title_receive,
        'date': date_receive,
        'time': time_receive,
        'max_count': max_count_receive,
        'category': category_receive,
        'content': content_receive,
        'author': '김철수',
        'joined_users': [1, 2],
        'created_at': datetime.now(timezone.utc) 
    }
  
  db.posts.insert_one(new_post)

  return render_template('post_card.html', post=new_post, categories=CATEGORIES)

@posts_bp.route('/new-modal')
def get_create_post_modal():
  return render_template('modals/create_post.html', categories=CATEGORIES)

@posts_bp.route('/profile-modal')
def get_profile_modal():
    user_payload = verify_token()
    if not user_payload:
      return "로그인이 필요합니다.", 401
    
    user = db.users.find_one({'user_id': user_payload['user_id']})
    return render_template('modals/profile.html', user=user)

# 라우트 추가
@posts_bp.route('/<post_id>/detail-modal')
def get_post_detail_modal(post_id):
  
  post = db.posts.find_one({'_id': ObjectId(post_id)})

  if not post:
    return "게시글을 찾을 수 없습니다.", 404
  return render_template('modals/post_detail.html', post=post)
  
@posts_bp.route('/<post_id>', methods=['DELETE'])
def delete_post(post_id):
  db.posts.delete_one({'_id': ObjectId(post_id)})
  return "", 200

@posts_bp.route('/<post_id>/edit')
def get_edit_form(post_id):
  post = db.posts.find_one({'_id': ObjectId(post_id)})
  curent_category = request.args.get('current_category', 'all')
  return render_template('/modals/post_edit_form.html', post=post, categories=CATEGORIES, curent_category=curent_category)

@posts_bp.route('/<post_id>', methods=['PATCH'])
def edit_post(post_id):
  title_receive = request.form['title']
  date_receive = request.form['date']
  time_receive = request.form['time']
  max_count_receive = request.form['max_count']
  content_receive = request.form['content']
  category_receive = request.form.get('category')

  current_category = request.args.get('current_category', 'all')

  db.posts.update_one(
    {'_id': ObjectId(post_id)},
    {'$set': {
        'title': title_receive,
        'date': date_receive,
        'time': time_receive,
        'max_count': max_count_receive,
        'category': category_receive,
        'content': content_receive
    }}
  )

  updated_post = db.posts.find_one({'_id': ObjectId(post_id)})

  if current_category != 'all' and updated_post['category'] != current_category:
    return "", 200

  return render_template('post_card.html', post=updated_post, categories=CATEGORIES)

@posts_bp.route('/update-nickname', methods=['PATCH'])
def update_nickname():
    new_nickname = request.form.get('user_nickname')

    print(user_id, new_nickname)
    response = db.users.update_one(
        {'user_id': user_id},
        {'$set': {'user_nickname': new_nickname}}
    )


    return "", 200
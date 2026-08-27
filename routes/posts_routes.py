from flask import Blueprint, render_template, abort, request, redirect, url_for, make_response
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

  if not user_payload:
    response = make_response(redirect(url_for('auth.get_login_page')))
    response.delete_cookie('access_token', path='/')
    return response
  
  user = db.users.find_one({'user_id': user_payload['user_id']})
  selected_category = request.args.get('category', 'all')

  if selected_category == 'all':
    posts = list(db.posts.find({}).sort('created_at', -1))
  elif selected_category== 'joined':
    posts = list(db.posts.find({'author' : user['_id']}).sort('created_at', -1))
  else:
    posts = list(db.posts.find({'category': selected_category}).sort('created_at', -1))

  today_str = datetime.now().strftime('%Y-%m-%d')
  filtered_posts = []

  for post in posts:
    joined_user_ids = post.get('joined_users', [])
    max_count = int(post.get('max_count', 0))
    post_date = post.get('date', '')  # 예: '2026-09-05'

    is_full = len(joined_user_ids) >= max_count  # 정원 초과 여부
    is_past = post_date < today_str               # 날짜 지남 여부

    if is_full or is_past:
        continue
    joined_user_ids = post.get('joined_users', [])

    post['is_joined'] = user['_id'] in joined_user_ids

    # 모달 로직과 동일하게 닉네임 리스트 추출
    joined_users_info = list(db.users.find({'_id': {'$in': joined_user_ids}}))
    post['joined_nicknames'] = [u.get('user_nickname', 'unknown') for u in joined_users_info]

    filtered_posts.append(post)



  return render_template('posts.html', posts=filtered_posts, current_category=selected_category, categories=CATEGORIES, filter_categories=FILTER_CATEGORIES, user=user)

@posts_bp.route('/', methods=['POST'])
def post_meeting():

  user_payload = verify_token()
  if not user_payload:
    return "로그인이 필요합니다.", 401
  
  # 2. 현재 로그인한 유저 정보 조회
  user = db.users.find_one({'user_id': user_payload['user_id']})

  
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
        'author': user['_id'],
        'joined_users': [user['_id']],
        'created_at': datetime.now(timezone.utc) 
    }
  
  db.posts.insert_one(new_post)

  new_post['is_joined'] = True
  new_post['joined_nicknames'] = [user.get('user_nickname', 'unknown')]

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
  author_user = db.users.find_one({'_id': post.get('author')})
  author_nickname = author_user.get('user_nickname', 'unknown') if author_user else 'unknown'

  joined_user_ids = post.get('joined_users', [])
  joined_users_info = list(db.users.find({'_id': {'$in': joined_user_ids}}))

  joined_nicknames = [u.get('user_nickname') for u in joined_users_info]


  user_payload = verify_token()
  if not user_payload:
    return "로그인이 필요합니다.", 401
  
  user = db.users.find_one({'user_id': user_payload['user_id']})
  user_id = user['_id']
  author_id = post['author']

  is_joined = user_id in joined_user_ids

  current_category = request.args.get('current_category', 'all')
  print('detail-modal')
  print(current_category)
  return render_template('modals/post_detail.html', current_category=current_category, category=post['category'], is_joined=is_joined, user_id=user_id, author_id = author_id, post=post, author_nickname=author_nickname, joined_nicknames=joined_nicknames, categories=CATEGORIES, filter_categories=FILTER_CATEGORIES)


@posts_bp.route('/<post_id>/join', methods=['POST'])
def join_post(post_id):
  # 1. 토큰 검증
  user_payload = verify_token()
  if not user_payload:
    return "로그인이 필요합니다.", 401
  
  # 2. 유저 및 게시글 조회
  user = db.users.find_one({'user_id': user_payload['user_id']})
  if not user:
    return "유저 정보를 찾을 수 없습니다.", 404

  user_id = user['_id']  # 👈 user_id 선언

  post = db.posts.find_one({'_id': ObjectId(post_id)})
  if not post:
    return "존재하지 않는 모임입니다.", 404

  joined_user_ids = post.get('joined_users', [])
  max_count = int(post.get('max_count', 0))

  # 3. 정원 초과 여부 검사 (선택 사항)
  if len(joined_user_ids) >= max_count:
    return "이미 정원이 가득 찬 모임입니다.", 400

  # 4. 참여 처리 (이미 참여 중이 아닌 경우에만)
  if user_id not in joined_user_ids:
    db.posts.update_one(
        {'_id': ObjectId(post_id)},
        {'$push': {'joined_users': user_id}}
    )

  # 5. 업데이트된 최신 모임 정보 및 참여자 닉네임 조회
  updated_post = db.posts.find_one({'_id': ObjectId(post_id)})
  joined_users_info = list(db.users.find({'_id': {'$in': updated_post.get('joined_users', [])}}))
  
  updated_post['is_joined'] = True
  updated_post['joined_nicknames'] = [u.get('user_nickname', 'unknown') for u in joined_users_info]

  current_category = request.args.get('current_category', 'all')

  # 6. 카드 UI 갱신을 위한 post_card.html 반환
  return render_template(
      'post_card.html',
      post=updated_post,
      categories=CATEGORIES,
      filter_categories=FILTER_CATEGORIES,
      current_category=current_category,
      user=user
  )

@posts_bp.route('/<post_id>/leave', methods=['POST'])
def leave_post(post_id):
  # 1. 로그인 토큰 검증
  user_payload = verify_token()
  if not user_payload:
    return "로그인이 필요합니다.", 401

  user = db.users.find_one({'user_id': user_payload['user_id']})
  if not user:
    return "유저 정보를 찾을 수 없습니다.", 404

  user_id = user['_id']
  post = db.posts.find_one({'_id': ObjectId(post_id)})
  if not post:
    return "존재하지 않는 모임입니다.", 404

  # 2. 방장은 취소할 수 없음 (작성자 보호)
  if post.get('author') == user_id:
    return "모임 작성자는 참여를 취소할 수 없습니다.", 400

  # 3. DB 배열(joined_users)에서 유저 _id 제거 ($pull)
  db.posts.update_one(
      {'_id': ObjectId(post_id)},
      {'$pull': {'joined_users': user_id}}
  )

  # 4. 최신 게시글 및 참여자 정보 조회
  updated_post = db.posts.find_one({'_id': ObjectId(post_id)})
  joined_users_info = list(db.users.find({'_id': {'$in': updated_post.get('joined_users', [])}}))

  updated_post['is_joined'] = False
  updated_post['joined_nicknames'] = [u.get('user_nickname', 'unknown') for u in joined_users_info]

  current_category = request.args.get('current_category', 'all')

  # 5. '참여 중' 탭에서 취소한 경우 카드 목록에서 즉시 지움 처리
  if current_category == 'joined':
    return "", 200

  # 6. 그 외 탭에서는 갱신된 카드 HTML 반환
  return render_template(
      'post_card.html',
      post=updated_post,
      categories=CATEGORIES,
      filter_categories=FILTER_CATEGORIES,
      current_category=current_category,
      user=user
  )


@posts_bp.route('/<post_id>', methods=['DELETE'])
def delete_post(post_id):
  db.posts.delete_one({'_id': ObjectId(post_id)})
  return "", 200

@posts_bp.route('/<post_id>/edit')
def get_edit_form(post_id):
  post = db.posts.find_one({'_id': ObjectId(post_id)})
  current_category = request.args.get('current_category', 'all')
  print('get')
  print(current_category)
  return render_template('/modals/post_edit_form.html', post=post, categories=CATEGORIES, current_category=current_category)

@posts_bp.route('/<post_id>', methods=['PATCH'])
def edit_post(post_id):
  title_receive = request.form['title']
  date_receive = request.form['date']
  time_receive = request.form['time']
  max_count_receive = request.form['max_count']
  content_receive = request.form['content']
  category_receive = request.form.get('category')

  current_category = request.args.get('current_category', 'all')
  print('patch')
  print(current_category)
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
    user_payload = verify_token()

    user_payload = verify_token()
    if not user_payload:
      return "로그인이 필요합니다.", 401
    
    user = db.users.find_one({'user_id': user_payload['user_id']})
    db.users.update_one(
        {'_id': user['_id']},
        {'$set': {'user_nickname': new_nickname}}
    )

    response = make_response("", 200)
    response.headers['HX-Redirect'] = '/posts'
    return response

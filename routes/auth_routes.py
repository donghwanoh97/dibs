# routes/auth_routes.py

import datetime
from datetime import timezone, timedelta
import jwt
# 임시 비밀번호 발급 기능을 위한 도구
import string
import random
import hashlib

from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database import db 

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = 'your_secret_key_here'

def verify_token():
    token = request.cookies.get('access_token')

    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# 0. 메인 페이지 렌더링(GET)
@auth_bp.route('/', methods=['GET'])
def get_main_page():
    user_payload = verify_token()

    if not user_payload:
        return redirect('/auth/login')

    return redirect('/')

# 1. 로그인 페이지 렌더링(GET)
@auth_bp.route('/login', methods=['GET'])
def get_login_page():
    user_payload = verify_token()

    if user_payload:
        return redirect(url_for('auth.get_main_page'))
    
    return render_template('login.html')

# 2. 회원가입 페이지 렌더링(GET) - 리다이렉트 추가
@auth_bp.route('/sign-up', methods=['GET'])
def get_signup_page():
    user_payload = verify_token()

    if user_payload:
        return redirect(url_for('auth.get_main_page'))

    return render_template('signup.html')

# 3. ID 찾기 페이지 렌더링(GET)
@auth_bp.route('/find-id', methods=['GET'])
def get_find_id_page():
    return render_template('find_id.html')

# 4. PW 찾기 페이지 렌더링(GET)
@auth_bp.route('/find-pw', methods=['GET'])
def get_find_pw_page():
    return render_template('find_pw.html')

# 5. 로그인 처리(POST) - JWT 발급 및 쿠키 저장
@auth_bp.route('/api/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id')
    input_password = request.form.get('password')

    user = db.users.find_one({'user_id': user_id})

    if user and check_password_hash(user['password'], input_password):
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.now(timezone.utc) + timedelta(hours=1)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        if isinstance(token, bytes):
            token = token.decode('utf-8')

        response = make_response(jsonify({'result': 'success', 'msg': '로그인 성공!'}))
        response.set_cookie('access_token', token, httponly=True, samesite='Lax', path='/')

        return response
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})    

# 6. 회원가입 처리(POST)
@auth_bp.route('/api/sign-up', methods=['POST'])
def signup():
    user_name = request.form.get('user_name')
    user_nickname = request.form.get('user_nickname')
    user_id = request.form.get('user_id')
    raw_password = request.form.get('password')

    if not all([user_name, user_nickname, user_id, raw_password]):
        return jsonify({'result': 'fail', 'msg': '모든 필수 항목을 입력해 주세요.'})
    
    if db.users.find_one({'user_id': user_id}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 아이디입니다.'})

    if db.users.find_one({'user_nickname': user_nickname}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 닉네임입니다.'})

    hashed_password = generate_password_hash(raw_password , method="pbkdf2:sha256")

    db.users.insert_one({
        'user_name': user_name, 
        'user_nickname': user_nickname, 
        'user_id': user_id, 
        'password': hashed_password
    })

    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})

# 7. ID 찾기 처리(POST)
@auth_bp.route('/api/find-id', methods=['POST'])
def find_id():
    user_name = request.form.get('user_name')
    user_nickname = request.form.get('user_nickname')

    if not user_name or not user_nickname:
        return jsonify({'result': 'fail', 'msg': '이름과 닉네임을 모두 입력해 주세요.'})

    user = db.users.find_one({
        'user_name': user_name,
        'user_nickname': user_nickname
    })

    if user:
        return jsonify({'result': 'success', 'user_id': user['user_id']})
    
    else:
        return jsonify({'result': 'fail', 'msg': '일치하는 회원 정보를 찾을 수 없습니다.'})

# 8. PW 찾기/재설정 처리(POST)
@auth_bp.route('/api/find-pw', methods=['POST'])
def find_pw():
    user_id = request.form.get('user_id')

    if not user_id:
        return jsonify({'result': 'fail', 'msg': '이메일을 입력해 주세요.'})

    user = db.users.find_one({'user_id' : user_id})

    if not user:
        return jsonify({'result': 'fail', 'msg': '등록되지 않은 이메일입니다.'})

    characters = string.ascii_letters + string.digits
    temp_password = ''.join(random.choice(characters) for _ in range(8))

    hashed_password = generate_password_hash(temp_password, method="pbkdf2:sha256")
    db.users.update_one({'user_id': user_id}, {'$set': {'password': hashed_password}})

    return jsonify({
        'result': 'success',
        'msg': f'임시 비밀번호가 발급되었습니다: {temp_password}\n로그인 후 비밀번호를 변경해 주세요.'
    })

# 9. 로그아웃 처리(POST)
@auth_bp.route('/api/log-out', methods=['POST'])
def logout():
    response = make_response(jsonify({'result': 'success', 'msg': '로그아웃되었습니다.'}))
    response.delete_cookie('access_token', path='/')

    return response

# 10. 비밀번호 재설정(POST)
@auth_bp.route('/api/rename-pw', methods=['POST'])
def rename_password_api():
    # 토큰 또는 세션에서 유저 식별자 확인 (JWT 토큰 쿠키 기준 예시)
    token_receive = request.cookies.get('mytoken')
    if not token_receive:
        return jsonify({'result': 'fail', 'msg': '로그인이 필요하거나 인증 세션이 만료되었습니다.'})
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['id']
        new_password = request.form.get('new_password')

        hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        db.users.update_one({'user_id': user_id}, {'$set': {'password': hashed_password}})

        return jsonify({'result': 'success', 'msg': '비밀번호가 성공적으로 변경되었습니다.'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '인증 토큰이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '유효하지 않은 토큰입니다.'})
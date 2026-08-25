# routes/auth_routes.py
from flask import Blueprint, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# database.py에서 db 객체 임포트
from database import db 

# 'auth' 블루프린트 생성
auth_bp = Blueprint('auth', __name__)

# 1. 로그인 페이지 렌더링(GET)
# 사용자가 접속(GET)하면 로그인 페이지를 브라우저에 렌더링
@auth_bp.route('/login', methods=['GET'])
def get_login_page():
    return render_template('login.html')

# 2. 회원가입 페이지 렌더링(GET)
# 사용자가 접속(GET)하면 회원가입 페이지를 브라우저에 렌더링
@auth_bp.route('/signup', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

# 3. 로그인 처리(POST)
@auth_bp.route('/api/login', methods=['POST'])
def login():
    # 사용자가 입력한 id와 password를 변수에 저장
    user_id = request.form.get('user_id')
    input_password = request.form.get('password')

    # DB에서 user_id에 해당하는 사용자 조회
    user = db.users.find_one({'user_id': user_id})

    # 사용자 존재 여부 및 비밀번호 암호화 검증
    if user and check_password_hash(user['password'], input_password):
    # 로그인 성공 (TODO: 추후 세션 저장(사용자가 로그인했음을 기억하는 기능) 추가 위치)
    # 로그인 성공 시 세션 또는 JWT 발급 처리 위치
        return jsonify({'result': 'success', 'msg': '로그인 성공!'})
    # 로그인 실패
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})    

# 4. 회원가입 처리(POST)
@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    # 사용자가 입력한 id와 password를 변수에 저장
    user_id = request.form.get('user_id')
    raw_password = request.form.get('password')

    # 아이디 중복 체크
    if db.users.find_one({'user_id': user_id}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 아이디입니다.'})

    # 비밀번호 단방향 암호화 (해시화)
    # 사용자가 입력한 원본 비밀번호(raw_password)를 복구할 수 없는 복잡한 문자열로 변환한 뒤 변수에 저장
    hashed_password = generate_password_hash(raw_password)

    # MongoDB 'users' 컬렉션에 회원 정보(user_id, hashed_password) 저장
    db.users.insert_one({'user_id': user_id, 'password': hashed_password})

    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})
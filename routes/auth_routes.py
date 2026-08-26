# routes/auth_routes.py

# 날짜와 시간 정보를 다루는 파이썬 기본 도구(JWT 토큰 만료 시간 설정에 필요)
import datetime
import jwt
# 임시 비밀번호 발급 기능을 위한 도구
import string
import random

from flask import Blueprint, render_template, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash

# database.py에서 db 객체 임포트
from database import db 

# 'auth' 블루프린트 생성
auth_bp = Blueprint('auth', __name__)

# 로그인 성공 후 사용자에게 전달되는 JWT를 검증하는 비밀키
# TODO: 추후 비밀키 외부 노출을 방지하기 위해 config 또는 외부 .env 파일로 관리 권장
SECRET_KEY = 'your_secret_key_here'

# 1. 로그인 페이지 렌더링(GET)
# 사용자가 접속(GET)하면 로그인 페이지를 브라우저에 렌더링
@auth_bp.route('/login', methods=['GET'])
def get_login_page():
    return render_template('login.html')

# 2. 회원가입 페이지 렌더링(GET)
# 사용자가 접속(GET)하면 회원가입 페이지를 브라우저에 렌더링
@auth_bp.route('/sign-up', methods=['GET'])
def get_signup_page():
    return render_template('signup.html')

# 3. ID 찾기 페이지 렌더링(GET)
# 사용자가 접속(GET)하면 ID 찾기 페이지를 브라우저에 렌더링
@auth_bp.route('/find-id', methods=['GET'])
def get_find_id_page():
    return render_template('find_id.html')

# 4. PW 찾기 페이지 렌더링(GET)
# 사용자가 접속(GET)하면 PW 찾기 페이지를 브라우저에 렌더링
@auth_bp.route('/find-pw', methods=['GET'])
def get_find_pw_page():
    return render_template('find_pw.html')

# 5. 로그인 처리(POST) - JWT 발급 및 쿠키 저장
@auth_bp.route('/api/login', methods=['POST'])
def login():
    # 사용자가 입력한 id와 password를 변수에 저장
    user_id = request.form.get('user_id')
    input_password = request.form.get('password')

    # DB에서 user_id에 해당하는 사용자 조회
    user = db.users.find_one({'user_id': user_id})

    # 사용자 존재 여부 및 비밀번호 암호화 검증
    # DB 조회 후 사용자 정보가 실제로 존재하는지, 입력받은 비밀번호가 암호화되어 저장된 비밀번호와 일치하는지 확인
    if user and check_password_hash(user['password'], input_password):
        # 로그인 성공 시 세션 또는 JWT 발급 처리

        # JWT 토큰에 담을 정보와 만료시간 지정
        payload = {
            # 이 토큰은 발급 후 1시간만 유효
            'user_id': user_id,
            # 현재 시간 + 1시간
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }

        # JWT 토큰 암호화 생성
        # payload: 토큰에 들어갈 유저 아이디와 만료 시간 정보
        # SECRET_KEY: 서버만 알고 있는 비밀 키
        # algorithm='HS256': 서명에 사용할 해시 알고리즘 방식
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # 브라우저에 로그인 성공 안내 메세지(JSON) 보낼 준비
        # 브라우저 저장소인 쿠키에 토큰을 전달
        response = make_response(jsonify({'result': 'success', 'msg': '로그인 성공!'}))

        # httponly=True: 악성 자바스크립트 공격(XSS)을 통한 토큰 탈취 방지
        # samesite='Lax': 악의적 요청(CSRF 공격) 방지 및 일반적 링크 이동 시 쿠키 전송 허용
        response.set_cookie('access_token', token, httponly=True, samesite='Lax')

        # 완성된 응답 객체(JSON 메시지 + 보안 쿠키 정보)를 브라우저로 전송해 로그인 처리 완료
        return response
    
    # 로그인 실패
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})    

# 6. 회원가입 처리(POST)
@auth_bp.route('/api/sign-up', methods=['POST'])
def signup():
    # 사용자가 입력한 id와 password를 변수에 저장
    user_name = request.form.get('user_name')
    user_nickname = request.form.get('user_nickname')
    user_id = request.form.get('user_id')
    raw_password = request.form.get('password')

    # 아이디 중복 체크
    if db.users.find_one({'user_id': user_id}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 아이디입니다.'})

    # 비밀번호 단방향 암호화 (해시화)
    # 사용자가 입력한 원본 비밀번호(raw_password)를 복구할 수 없는 복잡한 문자열로 변환한 뒤 변수에 저장
    hashed_password = generate_password_hash(raw_password)

    # MongoDB 'users' 컬렉션에 회원 정보(user_id, hashed_password) 저장
    db.users.insert_one({
        'user_name': user_name, 
        'user_nickname': user_nickname, 
        'user_id': user_id, 
        'password': hashed_password
    })

    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})

# 7. ID 찾기 처리(POST) -> 동명이인 대응 방법 (이름 + 닉네임 조회)
@auth_bp.route('/api/find-id', methods=['POST'])
def find_id():
    # 이름, 닉네임 저장
    user_name = request.form.get('user_name')
    user_nickname = request.form.get('user_nickname')

    # 만약에 이름을 입력하지 않았거나, 닉네임을 입력하지 않았다면
    if not user_name or not user_nickname:
        # 실패 메시지를 보내고 함수 종료
        return jsonify({'result': 'fail', 'msg': '이름과 닉네임을 모두 입력해 주세요.'})

    # 이름과 닉네임 동시 검증
    # DB의 users 목록에서 name과 nickname이 입력받은 값과 일치하는 사용자 1명을 찾아 저장
    user = db.users.find_one({
        'user_name': user_name,
        'user_nickname': user_nickname
    })

    # 만약 일치하는 사용자 정보를 찾았다면
    if user:
        # 성공 메시지를 보내고 user_id를 보여준다.
        return jsonify({'result': 'success', 'user_id': user['user_id']})
    
    # 찾지 못했다면
    else:
        # 실패 메시지를 보낸다.
        return jsonify({'result': 'fail', 'msg': '일치하는 회원 정보를 찾을 수 없습니다.'})

# 8. PW 찾기/재설정 처리(POST)
@auth_bp.route('/api/find-pw', methods=['POST'])
def find_pw():
    # 사용자의 ID를 가져와 변수에 저장

    # ID를 입력하지 않았을 경우 메시지 반환 후 함수 종료

    # DB에서 사용자 조회

    # 입력한 ID가 DB에 없는 경우 메시지 반환 후 함수 종료

    # 임시 비밀번호 생성 (8자리 영문 + 숫자)

    # DB에 암호화된 임시 비밀번호 업데이트

# 9. 로그아웃 처리(POST)
@auth_bp.route('/api/log-out', methods=['POST'])
def logout():
    # 응답 객체를 만들어 기존에 발급한 access_token 쿠키 삭제
    # 파이썬 딕셔너리 데이터를 브라우저가 이해 가능한 JSON 형태 데이터로 변환
    response = make_response(jsonify({'result': 'success', 'msg': '로그아웃되었습니다.'}))
    # 생성된 응답 객체에 브라우저에 저장되어 있는 특정 쿠키 삭제 명령
    response.delete_cookie('access_token')

    # 브라우저로 최종 반환
    return response
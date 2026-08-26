# routes/auth_routes.py

# 날짜와 시간 정보를 다루는 파이썬 기본 도구(JWT 토큰 만료 시간 설정에 필요)
# TODO(트러블슈팅): 회원가입 요청 중 500 내지 400번대 에러 발생 -> AJAX의 error 콜백 실행
# Flask 2.3 이상 버전에서 발생하는 모듈 미불러옴 오류
import datetime
from datetime import timezone, timedelta
import jwt
# 임시 비밀번호 발급 기능을 위한 도구
import string
import random

# [트러블슈팅 해결용 모듈 추가]: redirect, url_for (비로그인/로그인 사용자의 페이지 자동 리다이렉트 처리)
from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# database.py에서 db 객체 임포트
from database import db 

# 'auth' 블루프린트 생성
auth_bp = Blueprint('auth', __name__)

# 로그인 성공 후 사용자에게 전달되는 JWT를 검증하는 비밀키
# TODO: 추후 비밀키 외부 노출을 방지하기 위해 config 또는 외부 .env 파일로 관리 권장
SECRET_KEY = 'your_secret_key_here'

# 쿠키 내 JWT 토큰 유효성 검증 함수
# 사용자가 보낸 토큰이 진짜인지 확인하는 함수
def verify_token():
    # 변수에 토큰 저장
    token = request.cookies.get('access_token')

    # 만약 토큰이 변수에 없다면 None 반환 후 함수 종료
    if not token:
        return None

    # 예외가 발생할 가능성 대비 코드
    # 토큰을 해독 및 검증하는 과정에서 오류(토큰 만료 및 위조)가 날 수 있으므로
    # 프로그램에 해당 사항에도 멈추지 않고 안전하게 처리할 수 있는 대비 코드
    try:
        # 토큰 복호화 및 유효성 검증 결과 저장 (UTC 기준 만료 시각 자동 체크)
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        # 토큰 해독 정보 반환 후 함수 종료
        return payload

    # try 안에서 토큰 만료 에러(ExpiredSignatureError) 혹은
    # 토큰 형태/위조 에러(InvalidTokenError) 발생 시 실행
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        # 토큰이 만료되었거나 유효하지 않은 경우 None 반환 후 함수 종료
        return None

# 0. 메인 페이지 렌더링(GET) - 로그인 체크 후 비로그인 시 /login으로
# 자동 리다이렉트
@auth_bp.route('/', methods=['GET'])
def get_main_page():
    # 현재 접속한 사용자가 올바른 토큰을 가지고 있는지 확인
    user_payload = verify_token()

    # user_payload가 비어있다면 = 사용자가 로그인 하지 않았다면
    # 비로그인 상태일 경우 로그인 페이지로 이동
    if not user_payload:
        return redirect('/auth/login')

    # 로그인 상태인 경우 메인 페이지 렌더링
    return render_template('meetings.html', user_id=user_payload['user_id'])

# 1. 로그인 페이지 렌더링(GET)
# 이미 로그인된 경우 메인 페이지로 리다이렉트
@auth_bp.route('/login', methods=['GET'])
def get_login_page():
    user_payload = verify_token()

    # 이미 로그인된 상태라면 메인 페이지로 이동
    if user_payload:
        return redirect(url_for('auth.get_main_page'))
    
    return render_template('login.html')

# 2. 회원가입 페이지 렌더링(GET) - 리다이렉트 추가
# 사용자가 접속(GET)하면 회원가입 페이지를 브라우저에 렌더링
@auth_bp.route('/sign-up', methods=['GET'])
def get_signup_page():
    user_payload = verify_token()

    if user_payload:
        return redirect(url_for('auth.get_main_page'))

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
            # TODO(트러블슈팅): datetime.now() 사용 시 서버 시간과 JWT 규격(UCT) 간 시차가 발생해 발급 즉시 만료되는 현상 발생
            # 해결: datetime.timezone.utc를 명시해 만료 시간을 UTC 기준으로 일관되게 토큰 생성
            'exp': datetime.datetime.now(timezone.utc) + timedelta(hours=1)
        }

        # JWT 토큰 암호화 생성
        # payload: 토큰에 들어갈 유저 아이디와 만료 시간 정보
        # SECRET_KEY: 서버만 알고 있는 비밀 키
        # algorithm='HS256': 서명에 사용할 해시 알고리즘 방식

        # TODO(트러블슈팅): JWT 버전에 따른 토큰 리턴 자료형 타입 차이로 인해 오류 발생
        # PyJWT 1.x는 결과가 bytes 타입으로 나와 쿠키에 넣으려고 할 때 오류가 남
        # PyJWT 2.x는 str을 반환
        # 버전에 따라 반환 타입이 달라 환경이 바뀔 때 코드가 터짐

        # isinstance()로 bytes 타입 여부 검사 후 str로 명시적 디코딩
        # 사용자 정보(payload)와 비밀키(SECRET_KEY)를 HS256 알고리즘으로
        # 암호화하여 토큰 생성 후 변수에 저장
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # 토큰이 bytes 타입이면 str로 디코딩
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        # 브라우저에 로그인 성공 안내 메세지(JSON) 보낼 준비
        # 브라우저 저장소인 쿠키에 토큰을 전달
        response = make_response(jsonify({'result': 'success', 'msg': '로그인 성공!'}))

        # httponly=True: 악성 자바스크립트 공격(XSS)을 통한 토큰 탈취 방지
        # samesite='Lax': 악의적 요청(CSRF 공격) 방지 및 일반적 링크 이동 시 쿠키 전송 허용

        # TODO(트러블슈팅): 쿠키 보안 옵션 설정으로 인한 브라우저 쿠키 미전송 문제 발생
        # path 옵션 미지정 시 현재 요청 경로 기준 쿠키가 생성되어 타 경로 요청 시 쿠키 전송이 누락되는 현상 발생
        # 쿠키 범위가 제한되어 메인 페이지나 다른 경로로 이동했을 때 브라우저가 쿠키를 서버로 보내지 않아 로그인 안 됨 상태 버그 발생
        # path='/' 옵션을 명시해 전역 경로에서 접근 가능하도록 함
        response.set_cookie('access_token', token, httponly=True, samesite='Lax', path='/')

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

    # 필수값 체크
    if not all([user_name, user_nickname, user_id, raw_password]):
        return jsonify({'result': 'fail', 'msg': '모든 필수 항목을 입력해 주세요.'})
    
    # 아이디 중복 체크
    if db.users.find_one({'user_id': user_id}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 아이디입니다.'})

    # TODO(트러블슈팅): ID 찾기 API에서 user_name과 user_nickname의 조합으로 사용자를 찾는데
    # 닉네임 중복을 허용해 ID 찾기 시 동명이인+동일닉네임 사용자가 존재할 경우 잘못된 계정이 조회되는 문제 발생
    # 회원가입 시 닉네임 중복 검사를 추가
    if db.users.find_one({'user_nickname': user_nickname}):
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 닉네임입니다.'})


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
    user_id = request.form.get('user_id')

    # ID를 입력하지 않았을 경우 메시지 반환 후 함수 종료
    if not user_id:
        return jsonify({'result': 'fail', 'msg': '이메일을 입력해 주세요.'})

    # DB에서 사용자 조회
    user = db.users.find_one({'user_id' : user_id})

    # 입력한 ID가 DB에 없는 경우 메시지 반환 후 함수 종료
    if not user:
        return jsonify({'result': 'fail', 'msg': '등록되지 않은 이메일입니다.'})

    # 임시 비밀번호 생성 (8자리 영문 + 숫자)
    characters = string.ascii_letters + string.digits
    temp_password = ''.join(random.choice(characters) for _ in range(8))

    # DB에 암호화된 임시 비밀번호 업데이트
    hashed_password = generate_password_hash(temp_password)
    db.users.update_one({'user_id': user_id}, {'$set': {'password': hashed_password}})

    # TODO: 실제 서비스 시 Flask-Mail을 이용해 user_id(이메일)로 temp_password를 발급 전송
    # 현재는 인증번호 및 이메일 전송 기능 연동 전이므로 성공 메시지와 함께 임시 비밀번호를 반환하도록 처리
    return jsonify({
        'result': 'success',
        'msg': f'임시 비밀번호가 발급되었습니다: {temp_password}\n로그인 후 비밀번호를 변경해 주세요.'
    })

# 9. 로그아웃 처리(POST)
@auth_bp.route('/api/log-out', methods=['POST'])
def logout():
    # 응답 객체를 만들어 기존에 발급한 access_token 쿠키 삭제
    # 파이썬 딕셔너리 데이터를 브라우저가 이해 가능한 JSON 형태 데이터로 변환
    response = make_response(jsonify({'result': 'success', 'msg': '로그아웃되었습니다.'}))

    # 생성된 응답 객체에 브라우저에 저장되어 있는 특정 쿠키 삭제 명령
    # TODO(트러블슈팅): 로그아웃 시 클라이언트 쿠키 삭제 불완전 문제
    # 쿠키 삭제 시 생성 시점의 path 및 domain 옵션이 일치하지 않아 브라우저에서 쿠키 삭제 명령을 무시하는 현상
    # 쿠키 발급 조건과 동일하게 path='/' 옵션을 명시해 쿠키 삭제 보장
    response.delete_cookie('access_token', path='/')

    # 브라우저로 최종 반환
    return response
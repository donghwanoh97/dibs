from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
from database import db 

posts = [
    {
        "title": "저녁에 햄버거 같이 드실 분",
        "date": "2026-09-01",
        "time": "18:00",
        "joined_users": [1, 2],
        "max_count": 4,
        "author": 1,
        "category": "meal",
        "content": "햄버거 같이 드실 분 구합니다. 버거킹 좋아하시는 분 환영. 냠",
        "created_at": "2026-08-26T03:51:59.232Z"
    },
    {
        "title": "주말 점심 파스타 맛집 같이 갈 분",
        "date": "2026-09-05",
        "time": "12:30",
        "joined_users": [3],
        "max_count": 3,
        "author": 3,
        "category": "meal",
        "content": "생면 파스타 맛집 예약해뒀습니다. 같이 맛있는 점심 드실 분 구해요!",
        "created_at": "2026-08-26T03:51:59.232Z"
    },
    {
        "title": "퇴근 후 초밥 스터디(?) 겸 저녁 모임",
        "date": "2026-09-03",
        "time": "19:00",
        "joined_users": [2, 4],
        "max_count": 4,
        "author": 2,
        "category": "meal",
        "content": "강남역 근처 스시집에서 저녁 먹으면서 소소하게 이야기 나눠요.",
        "created_at": "2026-08-26T03:51:59.232Z"
    },
    {
        "title": "CS 기초(운영체제/네트워크) 주말 스터디원 모집",
        "date": "2026-09-06",
        "time": "14:00",
        "joined_users": [1],
        "max_count": 5,
        "author": 1,
        "category": "study",
        "content": "컴퓨터 사이언스 핵심 전공지식 복습 스터디입니다. 매주 온/오프라인으로 진행합니다.",
        "created_at": "2026-08-26T03:51:59.232Z"
    },
    {
        "title": "알고리즘 & 자료구조 문제 풀이 모임",
        "date": "2026-09-08",
        "time": "20:00",
        "joined_users": [5, 6],
        "max_count": 4,
        "author": 5,
        "category": "study",
        "content": "백준/프로그래머스 골드 난이도 문제 하루 1개씩 풀고 온라인 코드 리뷰 진행합니다.",
        "created_at": "2026-08-26T03:51:59.232Z"
    },
    {
        "title": "냠",
        "date": "2026-09-05",
        "time": "19:21",
        "max_count": 55,
        "category": "study",
        "content": "안녕",
        "author": "김철수",
        "joined_users": [1, 2],
        "created_at": "2026-08-26T05:21:43.022Z"
    }
]


# 기존 데이터 삭제
db.posts.delete_many({})

# 더미 데이터 삽입
db.posts.insert_many(posts)

print(f"{len(posts)}개의 더미 데이터를 삽입했습니다.")

# 회원가입 규칙(영문+숫자 8자 이상)을 만족하는 기본 비밀번호 해시 생성 ("test1234!")
common_password_hash = generate_password_hash("test1234!", method="pbkdf2:sha256")

# 회원가입 폼 구조에 맞춘 유저 더미 데이터 목록
users = [
    {
        "user_name": "오동환",
        "user_nickname": "동12",
        "user_id": "a@a.com",
        "password": "pbkdf2:sha256:1000000$0EcHo6GxSPVBUXWQ$0eb79a90109f4738e501021493d22eff6cd73e987c948f8c3a8e99be7c8c3116",
    },
    {
        "user_name": "오동환",
        "user_nickname": "동동",
        "user_id": "aaa",
        "password": "pbkdf2:sha256:1000000$P6SYiWc54B6kqndv$2ba7ffbe8edf4b50f8ccac31d4acf5aa3973003a0836787ba6288e12ac6cf2b4",
    },
    {
        "user_name": "김철수",
        "user_nickname": "철수왕",
        "user_id": "chulsoo@test.com",
        "password": common_password_hash,
    },
    {
        "user_name": "이영희",
        "user_nickname": "영희네",
        "user_id": "younghee@test.com",
        "password": common_password_hash,
    },
    {
        "user_name": "박민수",
        "user_nickname": "민수코딩",
        "user_id": "minsu@test.com",
        "password": common_password_hash,
    },
    {
        "user_name": "정수진",
        "user_nickname": "수진스",
        "user_id": "sujin@test.com",
        "password": common_password_hash,
    },
    {
        "user_name": "최현우",
        "user_nickname": "현우짱",
        "user_id": "hyunwoo@test.com",
        "password": common_password_hash,
    },
    {
        "user_name": "강지민",
        "user_nickname": "지민키친",
        "user_id": "jimin@test.com",
        "password": common_password_hash,
    },
]

# 기존 유저 데이터 초기화 및 신규 더미 데이터 삽입
db.users.delete_many({})
result = db.users.insert_many(users)

print(f"{len(result.inserted_ids)}명의 유저 더미 데이터를 성공적으로 삽입했습니다.")
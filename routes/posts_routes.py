from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from pymongo import MongoClient
from datetime import datetime, timezone

posts_bp = Blueprint('posts', __name__, template_folder = 'templates')

client = MongoClient('localhost', 27017)
from database import db 

db.posts.insert_one({'title': '저녁에 햄버거 같이 드실 분', 'date': '2026-09-01', 'time': '18:00', 'joined_users' : [1, 2], 'max_count': 4, 'author': 1, 'category' : '식사', 'content': '햄버거 같이 드실 분 구합니다. 버거킹 좋아하시는 분 환영.'})

posts_data = [
    # 식사 카테고리 (3개)
    {
        "title": "저녁에 햄버거 같이 드실 분",
        "date": "2026-09-01",
        "time": "18:00",
        "joined_users": [1, 2],
        "max_count": 4,
        "author": 1,
        "category": "식사",
        "content": "햄버거 같이 드실 분 구합니다. 버거킹 좋아하시는 분 환영.",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "title": "주말 점심 파스타 맛집 같이 갈 분",
        "date": "2026-09-05",
        "time": "12:30",
        "joined_users": [3],
        "max_count": 3,
        "author": 3,
        "category": "식사",
        "content": "생면 파스타 맛집 예약해뒀습니다. 같이 맛있는 점심 드실 분 구해요!",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "title": "퇴근 후 초밥 스터디(?) 겸 저녁 모임",
        "date": "2026-09-03",
        "time": "19:00",
        "joined_users": [2, 4],
        "max_count": 4,
        "author": 2,
        "category": "식사",
        "content": "강남역 근처 스시집에서 저녁 먹으면서 소소하게 이야기 나눠요.",
        "created_at": datetime.now(timezone.utc)
    },

    # 공부 (컴퓨터 사이언스) 카테고리 (2개)
    {
        "title": "CS 기초(운영체제/네트워크) 주말 스터디원 모집",
        "date": "2026-09-06",
        "time": "14:00",
        "joined_users": [1],
        "max_count": 5,
        "author": 1,
        "category": "공부",
        "content": "컴퓨터 사이언스 핵심 전공지식 복습 스터디입니다. 매주 온/오프라인으로 진행합니다.",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "title": "알고리즘 & 자료구조 문제 풀이 모임",
        "date": "2026-09-08",
        "time": "20:00",
        "joined_users": [5, 6],
        "max_count": 4,
        "author": 5,
        "category": "공부",
        "content": "백준/프로그래머스 골드 난이도 문제 하루 1개씩 풀고 온라인 코드 리뷰 진행합니다.",
        "created_at": datetime.now(timezone.utc)
    }
]

db.posts.drop()
db.posts.insert_many(posts_data)

@posts_bp.route('/')
def get_posts():
  selected_category = request.args.get('category', '전체')

  if selected_category == '전체':
    posts = list(db.posts.find({}, {'_id': False}))
  else:
    posts = list(db.posts.find({'category': selected_category}, {'_id': False}))

  return render_template('posts.html', posts=posts, current_category=selected_category)

#@posts_bp.route('/', methods=['POST'])
#def post_meeting():

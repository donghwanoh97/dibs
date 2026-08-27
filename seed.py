from werkzeug.security import generate_password_hash
from database import db

# 1. 공통 비밀번호 해시 생성
common_password_hash = generate_password_hash(
    "test1234!", method="pbkdf2:sha256"
)

# 2. 유저 더미 데이터
users = [
    {
        "user_name": "오동환",
        "user_nickname": "동동",
        "user_id": "aaa",
        "password": "pbkdf2:sha256:1000000$P6SYiWc54B6kqndv$2ba7ffbe8edf4b50f8ccac31d4acf5aa3973003a0836787ba6288e12ac6cf2b4",
    },
    {
        "user_name": "김철수",
        "user_nickname": "철수왕",
        "user_id": "chulsoo",
        "password": common_password_hash,
    },
    {
        "user_name": "이영희",
        "user_nickname": "영희네",
        "user_id": "younghee",
        "password": common_password_hash,
    },
    {
        "user_name": "박민수",
        "user_nickname": "민수코딩",
        "user_id": "minsu",
        "password": common_password_hash,
    },
    {
        "user_name": "정수진",
        "user_nickname": "수진스",
        "user_id": "sujin",
        "password": common_password_hash,
    },
    {
        "user_name": "최현우",
        "user_nickname": "현우짱",
        "user_id": "hyunwoo",
        "password": common_password_hash,
    },
    {
        "user_name": "강지민",
        "user_nickname": "지민키친",
        "user_id": "jimin",
        "password": common_password_hash,
    },
]

# 기존 유저 초기화 및 삽입
db.users.delete_many({})
user_result = db.users.insert_many(users)

print(f"{len(user_result.inserted_ids)}명의 유저 더미 데이터를 성공적으로 삽입했습니다.")

# user_id -> ObjectId 매핑
user_map = {
    user["user_id"]: user["_id"]
    for user in db.users.find()
}


# 3. 게시글 더미 데이터
posts = [

    # ============================================================
    # 식사 모임
    # ============================================================

    {
        "title": "오늘 저녁 같이 먹고 가실 분 🍚",
        "date": "2026-08-28",
        "time": "18:30",
        "joined_users": [
            user_map["aaa"],
            user_map["chulsoo"]
        ],
        "max_count": 4,
        "author": user_map["aaa"],
        "category": "meal",
        "content": "수업 끝나고 근처에서 저녁 먹으려고 합니다. 같이 편하게 식사하실 분 구해요!",
        "created_at": "2026-08-27T03:10:00.000Z",
    },

    {
        "title": "점심에 돈까스 드실 분 계신가요?",
        "date": "2026-08-28",
        "time": "12:30",
        "joined_users": [
            user_map["younghee"]
        ],
        "max_count": 3,
        "author": user_map["younghee"],
        "category": "meal",
        "content": "점심시간에 학교 근처 돈까스집 가려고 해요. 혼밥하기 아쉬워서 같이 드실 분 찾아요!",
        "created_at": "2026-08-27T02:40:00.000Z",
    },

    {
        "title": "퇴근 후 치맥 한잔 하실 분 🍗",
        "date": "2026-08-29",
        "time": "19:00",
        "joined_users": [
            user_map["chulsoo"],
            user_map["minsu"]
        ],
        "max_count": 4,
        "author": user_map["chulsoo"],
        "category": "meal",
        "content": "이번 주도 고생한 기념으로 가볍게 치킨 먹으려고 합니다. 편하게 이야기하면서 드실 분!",
        "created_at": "2026-08-26T09:20:00.000Z",
    },

    {
        "title": "주말에 파스타 맛집 같이 가요 🍝",
        "date": "2026-08-30",
        "time": "12:00",
        "joined_users": [
            user_map["minsu"],
            user_map["sujin"]
        ],
        "max_count": 4,
        "author": user_map["minsu"],
        "category": "meal",
        "content": "주말 점심에 새로 생긴 파스타집 가보려고 합니다. 맛집 좋아하시는 분 환영해요!",
        "created_at": "2026-08-26T08:15:00.000Z",
    },

    {
        "title": "저녁에 마라탕 같이 드실 분",
        "date": "2026-09-01",
        "time": "18:00",
        "joined_users": [
            user_map["jimin"]
        ],
        "max_count": 3,
        "author": user_map["jimin"],
        "category": "meal",
        "content": "퇴근하고 마라탕 먹으러 가려고 합니다. 맵찔이도 환영합니다 😋",
        "created_at": "2026-08-27T04:30:00.000Z",
    },


    # ============================================================
    # 공부 모임
    # ============================================================

    {
        "title": "주말에 CS 같이 공부하실 분",
        "date": "2026-08-29",
        "time": "14:00",
        "joined_users": [
            user_map["aaa"]
        ],
        "max_count": 4,
        "author": user_map["aaa"],
        "category": "study",
        "content": "운영체제와 네트워크 위주로 각자 공부하고 모르는 내용 같이 정리해보려고 합니다.",
        "created_at": "2026-08-27T01:20:00.000Z",
    },

    {
        "title": "알고리즘 문제 같이 풀어요 💻",
        "date": "2026-08-30",
        "time": "15:00",
        "joined_users": [
            user_map["sujin"],
            user_map["hyunwoo"]
        ],
        "max_count": 4,
        "author": user_map["sujin"],
        "category": "study",
        "content": "백준이나 프로그래머스 문제 각자 풀고 풀이 공유하는 방식으로 진행하려고 합니다.",
        "created_at": "2026-08-26T07:45:00.000Z",
    },

    {
        "title": "프론트엔드 면접 준비 같이 하실 분",
        "date": "2026-09-01",
        "time": "19:30",
        "joined_users": [
            user_map["hyunwoo"]
        ],
        "max_count": 4,
        "author": user_map["hyunwoo"],
        "category": "study",
        "content": "JavaScript와 React 중심으로 면접 예상 질문을 서로 내주면서 준비해보려고 합니다.",
        "created_at": "2026-08-27T03:35:00.000Z",
    },

    {
        "title": "자격증 공부 같이 하실 분 📖",
        "date": "2026-09-03",
        "time": "18:30",
        "joined_users": [
            user_map["jimin"],
            user_map["younghee"]
        ],
        "max_count": 5,
        "author": user_map["jimin"],
        "category": "study",
        "content": "혼자 하면 자꾸 미루게 돼서 같이 공부하실 분을 구합니다. 각자 공부 후 간단하게 인증해요!",
        "created_at": "2026-08-27T02:50:00.000Z",
    },

    {
        "title": "개발자 취업 준비 스터디",
        "date": "2026-09-05",
        "time": "13:00",
        "joined_users": [
            user_map["aaa"],
            user_map["chulsoo"],
            user_map["minsu"]
        ],
        "max_count": 4,
        "author": user_map["chulsoo"],
        "category": "study",
        "content": "취업 준비하면서 서로 정보 공유하고 모의 면접이나 코드 리뷰도 같이 진행해보려고 합니다.",
        "created_at": "2026-08-26T06:30:00.000Z",
    },


    # ============================================================
    # 모집 마감 상태
    # ============================================================

    {
        "title": "주말 브런치 같이 먹어요",
        "date": "2026-08-30",
        "time": "11:30",
        "joined_users": [
            user_map["younghee"],
            user_map["sujin"],
            user_map["jimin"]
        ],
        "max_count": 3,
        "author": user_map["younghee"],
        "category": "meal",
        "content": "주말에 브런치 먹으면서 여유롭게 이야기 나누실 분들을 모집했어요.",
        "created_at": "2026-08-26T05:40:00.000Z",
    },

    {
        "title": "React 기초 복습 스터디",
        "date": "2026-09-02",
        "time": "20:00",
        "joined_users": [
            user_map["aaa"],
            user_map["hyunwoo"],
            user_map["sujin"]
        ],
        "max_count": 3,
        "author": user_map["aaa"],
        "category": "study",
        "content": "React 컴포넌트와 상태 관리 부분을 같이 복습하고 간단한 실습도 진행합니다.",
        "created_at": "2026-08-26T04:50:00.000Z",
    },


    # ============================================================
    # 내 참여 모임 테스트
    # ============================================================

    {
        "title": "퇴근하고 저녁 먹으면서 이야기해요",
        "date": "2026-09-04",
        "time": "19:00",
        "joined_users": [
            user_map["aaa"],
            user_map["jimin"]
        ],
        "max_count": 4,
        "author": user_map["jimin"],
        "category": "meal",
        "content": "가볍게 저녁 먹으면서 요즘 하는 일이나 관심사 이야기해요.",
        "created_at": "2026-08-27T04:10:00.000Z",
    },


    # ============================================================
    # 과거 모임
    # ============================================================

    {
        "title": "지난주에 같이 먹었던 국밥 모임",
        "date": "2026-08-23",
        "time": "12:00",
        "joined_users": [
            user_map["aaa"],
            user_map["chulsoo"]
        ],
        "max_count": 4,
        "author": user_map["chulsoo"],
        "category": "meal",
        "content": "지난 주말에 같이 국밥 먹었던 모임입니다.",
        "created_at": "2026-08-22T03:30:00.000Z",
    },

    {
        "title": "JavaScript 스터디 1회차",
        "date": "2026-08-25",
        "time": "19:00",
        "joined_users": [
            user_map["aaa"],
            user_map["sujin"],
            user_map["hyunwoo"]
        ],
        "max_count": 4,
        "author": user_map["sujin"],
        "category": "study",
        "content": "JavaScript 기본 문법과 실행 컨텍스트를 같이 공부했습니다.",
        "created_at": "2026-08-24T02:00:00.000Z",
    },


    # ============================================================
    # 여유 있게 남아있는 모집
    # ============================================================

    {
        "title": "토요일 오후 카페에서 공부해요 ☕",
        "date": "2026-09-05",
        "time": "14:00",
        "joined_users": [
            user_map["minsu"]
        ],
        "max_count": 5,
        "author": user_map["minsu"],
        "category": "study",
        "content": "각자 할 일 가져와서 카페에서 같이 공부하려고 합니다. 조용히 공부하실 분 환영해요!",
        "created_at": "2026-08-27T03:50:00.000Z",
    },

    {
        "title": "점심에 김치찌개 먹으러 가요",
        "date": "2026-09-02",
        "time": "12:30",
        "joined_users": [],
        "max_count": 4,
        "author": user_map["aaa"],
        "category": "meal",
        "content": "점심시간에 근처 맛집에서 김치찌개 먹으려고 합니다. 같이 드실 분 편하게 들어오세요!",
        "created_at": "2026-08-27T05:00:00.000Z",
    },
]


# 4. 기존 게시글 초기화 및 신규 게시글 삽입
db.posts.delete_many({})

post_result = db.posts.insert_many(posts)

print(
    f"{len(post_result.inserted_ids)}개의 게시글 더미 데이터를 "
    "성공적으로 삽입했습니다."
)
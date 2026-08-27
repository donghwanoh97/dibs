from werkzeug.security import generate_password_hash
from database import db

# 1. 공통 비밀번호 해시 생성 ("test1234!")
common_password_hash = generate_password_hash(
    "test1234!", method="pbkdf2:sha256"
)

# 2. 유저 더미 데이터 정의
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

# 3. 기존 유저 데이터 초기화 및 신규 유저 삽입
db.users.delete_many({})
user_result = db.users.insert_many(users)
print(f"{len(user_result.inserted_ids)}명의 유저 더미 데이터를 성공적으로 삽입했습니다.")

# 4. DB에 저장된 유저의 user_id -> ObjectId 매핑 딕셔너리 생성
user_map = {user["user_id"]: user["_id"] for user in db.users.find()}

# 5. 게시글 데이터 작성 (유저 ObjectId 연동 + 필터링 테스트케이스 추가)
posts = [
    # --- 기존 데이터 ---
    {
        "title": "저녁에 햄버거 같이 드실 분",
        "date": "2026-09-01",
        "time": "18:00",
        "joined_users": [user_map["aaa"], user_map["chulsoo"]],
        "max_count": 4,
        "author": user_map["aaa"],
        "category": "meal",
        "content": "햄버거 같이 드실 분 구합니다. 버거킹 좋아하시는 분 환영. 냠",
        "created_at": "2026-08-26T03:51:59.232Z",
    },
    {
        "title": "주말 점심 파스타 맛집 같이 갈 분",
        "date": "2026-09-05",
        "time": "12:30",
        "joined_users": [user_map["younghee"]],
        "max_count": 3,
        "author": user_map["younghee"],
        "category": "meal",
        "content": "생면 파스타 맛집 예약해뒀습니다. 같이 맛있는 점심 드실 분 구해요!",
        "created_at": "2026-08-26T03:51:59.232Z",
    },
    {
        "title": "퇴근 후 초밥 스터디(?) 겸 저녁 모임",
        "date": "2026-09-03",
        "time": "19:00",
        "joined_users": [user_map["chulsoo"], user_map["minsu"]],
        "max_count": 4,
        "author": user_map["chulsoo"],
        "category": "meal",
        "content": "강남역 근처 스시집에서 저녁 먹으면서 소소하게 이야기 나눠요.",
        "created_at": "2026-08-26T03:51:59.232Z",
    },
    {
        "title": "CS 기초(운영체제/네트워크) 주말 스터디원 모집",
        "date": "2026-09-06",
        "time": "14:00",
        "joined_users": [user_map["aaa"]],
        "max_count": 5,
        "author": user_map["aaa"],
        "category": "study",
        "content": "컴퓨터 사이언스 핵심 전공지식 복습 스터디입니다. 매주 온/오프라인으로 진행합니다.",
        "created_at": "2026-08-26T03:51:59.232Z",
    },
    {
        "title": "알고리즘 & 자료구조 문제 풀이 모임",
        "date": "2026-09-08",
        "time": "20:00",
        "joined_users": [user_map["sujin"], user_map["hyunwoo"]],
        "max_count": 4,
        "author": user_map["sujin"],
        "category": "study",
        "content": "백준/프로그래머스 골드 난이도 문제 하루 1개씩 풀고 온라인 코드 리뷰 진행합니다.",
        "created_at": "2026-08-26T03:51:59.232Z",
    },
    {
        "title": "냠",
        "date": "2026-09-05",
        "time": "19:21",
        "max_count": 55,
        "category": "study",
        "content": "안녕",
        "author": user_map["chulsoo"],
        "joined_users": [user_map["aaa"], user_map["chulsoo"]],
        "created_at": "2026-08-26T05:21:43.022Z",
    },

    # --- [테스트용 신규 데이터] 필터링 검증 데이터 6종 ---
    {
        "title": "[테스트] 이미 날짜가 지난 모임 (과거)",
        "date": "2026-08-01",
        "time": "12:00",
        "joined_users": [user_map["younghee"]],
        "max_count": 4,
        "author": user_map["younghee"],
        "category": "meal",
        "content": "지난 달 모임 테스트용 데이터입니다. (is_past = True 걸러져야 함)",
        "created_at": "2026-08-01T00:00:00.000Z",
    },
    {
        "title": "[테스트] 정원 만원 마감 모임 (인원 초과)",
        "date": "2026-09-10",
        "time": "15:00",
        "joined_users": [user_map["chulsoo"], user_map["younghee"]],
        "max_count": 2,  # 2명 참여 중 / 최대 2명
        "author": user_map["chulsoo"],
        "category": "study",
        "content": "정원이 다 찬 모임입니다. (is_full = True 걸러져야 함)",
        "created_at": "2026-08-26T06:00:00.000Z",
    },
    {
        "title": "[테스트] 내일 진행되는 따끈따끈한 스터디",
        "date": "2026-08-28",
        "time": "10:00",
        "joined_users": [user_map["jimin"]],
        "max_count": 3,
        "author": user_map["jimin"],
        "category": "study",
        "content": "오늘 기준 내일 날짜 모임입니다. (정상 노출되어야 함)",
        "created_at": "2026-08-27T01:00:00.000Z",
    },
    {
        "title": "[테스트] 정원 1명 남은 벼락치기 파스타 모임",
        "date": "2026-08-30",
        "time": "13:00",
        "joined_users": [user_map["minsu"], user_map["sujin"]],
        "max_count": 3,  # 2명 참여 중 / 최대 3명
        "author": user_map["minsu"],
        "category": "meal",
        "content": "마지막 한 자리 남아있는 식사 모임입니다.",
        "created_at": "2026-08-27T02:00:00.000Z",
    },
    {
        "title": "[테스트] 내(aaa)가 작성자인데 정원이 꽉 찬 모임",
        "date": "2026-09-15",
        "time": "19:00",
        "joined_users": [user_map["aaa"], user_map["hyunwoo"]],
        "max_count": 2,
        "author": user_map["aaa"],
        "category": "study",
        "content": "내가 만든 방이지만 정원은 꽉 참. (내가 작성한 모임 예외 처리 테스트용)",
        "created_at": "2026-08-27T03:00:00.000Z",
    },
    {
        "title": "[테스트] 내(aaa)가 참여 중인데 날짜가 지난 모임",
        "date": "2026-08-10",
        "time": "18:00",
        "joined_users": [user_map["aaa"], user_map["chulsoo"]],
        "max_count": 5,
        "author": user_map["chulsoo"],
        "category": "meal",
        "content": "내가 과거에 참여했던 모임. (참여 중 탭에서의 과거 모임 노출 여부 테스트용)",
        "created_at": "2026-08-10T00:00:00.000Z",
    },
]

# 6. 기존 게시글 초기화 및 신규 게시글 삽입
db.posts.delete_many({})
post_result = db.posts.insert_many(posts)
print(f"{len(post_result.inserted_ids)}개의 게시글 더미 데이터를 성공적으로 삽입했습니다.")
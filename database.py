# database.py
from pymongo import MongoClient

# 로컬 MongoDB 연결
# TODO: AWS 배포 시 연결 문자열(URI)만 환경변수 등으로 교체
client = MongoClient('mongodb://localhost:27017/')

# 사용할 데이터베이스명 지정
db = client['dibs_db']
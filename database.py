import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 환경변수가 없을 경우 기본 로컬 MongoDB 사용
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)

db = client['dibs_db']
from database import db

# 모든 데이터 삭제
result = db.users.delete_many({})

print(f"삭제된 사용자 수: {result.deleted_count}명")
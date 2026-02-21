from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

uri = "mongodb+srv://wordycow0001_db_user:wZMqQeXV7LbG79IM@cluster0.728c79v.mongodb.net/?appName=Cluster0"

# 새 버전 (leemay)
uri = "mongodb+srv://leemay:thgus1106@cluster0.728c79v.mongodb.net/?appName=Cluster0"

print("=" * 60)
print("🤖 이메이(Emay) - MongoDB 연결 테스트")
print("=" * 60)

# MongoDB 클라이언트 생성
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    # 연결 테스트
    client.admin.command('ping')
    print("✅ MongoDB Atlas 연결 성공!")
    print()
    
    # 데이터베이스 및 컬렉션 생성
    db = client["emay_database"]
    users = db["users"]
    
    print("📊 데이터베이스: emay_database")
    print("📋 컬렉션: users")
    print()
    
    # 이메이 시스템 정보 추가
    emay_system = {
        "name": "이메이",
        "type": "AI_Companion",
        "version": "1.0.0",
        "created_at": datetime.now(),
        "personality": {
            "traits": ["친근함", "공감적", "도움이 되는"],
            "tone": "따뜻하고 친구 같은"
        },
        "capabilities": [
            "일상 대화",
            "감정 인식",
            "개인 정보 기억",
            "이미지 생성",
            "문서 분석"
        ],
        "platforms": ["telegram", "discord"],
        "status": "initialized"
    }
    
    result = users.insert_one(emay_system)
    print(f"✅ 이메이 시스템 등록 완료!")
    print(f"   ID: {result.inserted_id}")
    print()
    
    # 테스트 사용자 추가
    test_user = {
        "user_id": "test_001",
        "name": "테스트 유저",
        "platform": "telegram",
        "joined_at": datetime.now(),
        "profile": {
            "hobbies": ["AI 개발", "코딩"],
            "personality": "호기심 많고 열정적"
        },
        "conversation_count": 0,
        "last_interaction": datetime.now()
    }
    
    result2 = users.insert_one(test_user)
    print(f"✅ 테스트 사용자 등록 완료!")
    print(f"   ID: {result2.inserted_id}")
    print()
    
    # 저장된 데이터 확인
    print("=" * 60)
    print("📋 데이터베이스에 저장된 사용자 목록:")
    print("=" * 60)
    
    for user in users.find():
        print(f"\n📌 이름: {user['name']}")
        print(f"   타입: {user.get('type', 'user')}")
        print(f"   ID: {user['_id']}")
        if 'capabilities' in user:
            print(f"   기능: {', '.join(user['capabilities'][:3])}...")
    
    print()
    print("=" * 60)
    print("🎉 MongoDB Atlas 설정 완료!")
    print("=" * 60)
    print()
    print("✨ 다음 단계:")
    print("   1. 메모리 시스템 구축")
    print("   2. LangChain 연동")
    print("   3. 텔레그램 봇 연결")
    print()

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print()
    print("🔧 해결 방법:")
    print("   1. 비밀번호가 올바른지 확인")
    print("   2. 인터넷 연결 확인")
    print("   3. pymongo 설치 확인: python -m pip install pymongo[srv]")
    print()

finally:
    client.close()
    print("👋 연결 종료")

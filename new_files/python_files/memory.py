from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from typing import List, Dict, Optional

class EmayMemory:
    """
    이메이의 기억 시스템
    - 사용자 정보 저장 및 조회
    - 대화 내역 기록
    - 감정 상태 추적
    - 중요한 정보 기억 (이름, 생일, 취미 등)
    """
    
    def __init__(self):
        # MongoDB 연결
        uri = "mongodb+srv://leemay:thgus1106@cluster0.728c79v.mongodb.net/?appName=Cluster0"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        
        # 데이터베이스 및 컬렉션
        self.db = self.client["emay_database"]
        self.users = self.db["users"]
        self.conversations = self.db["conversations"]
        self.memories = self.db["memories"]
        
        print("✅ 이메이 메모리 시스템 초기화 완료")
    
    # === 사용자 관리 ===
    
    def save_user(self, user_id: str, name: str, platform: str = "telegram") -> Dict:
        """새로운 사용자 등록 또는 업데이트"""
        user_data = {
            "user_id": user_id,
            "name": name,
            "platform": platform,
            "joined_at": datetime.now(),
            "last_interaction": datetime.now(),
            "profile": {
                "hobbies": [],
                "personality": "",
                "important_dates": {},
                "preferences": {}
            },
            "stats": {
                "conversation_count": 0,
                "total_messages": 0,
                "favorite_topics": []
            },
            "emotional_state": {
                "current": "중립",
                "history": []
            }
        }
        
        # 기존 사용자 확인
        existing = self.users.find_one({"user_id": user_id})
        
        if existing:
            # 마지막 대화 시간만 업데이트
            self.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_interaction": datetime.now()}}
            )
            print(f"👋 반가워요, {name}님! 다시 만나서 기뻐요!")
            return existing
        else:
            # 새 사용자 등록
            self.users.insert_one(user_data)
            print(f"🎉 환영합니다, {name}님! 처음 뵙겠어요. 앞으로 잘 부탁드려요!")
            return user_data
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """사용자 정보 조회"""
        return self.users.find_one({"user_id": user_id})
    
    def update_user_profile(self, user_id: str, field: str, value):
        """사용자 프로필 업데이트"""
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {f"profile.{field}": value}}
        )
        print(f"✅ {field} 정보가 기억되었어요!")
    
    def add_hobby(self, user_id: str, hobby: str):
        """취미 추가"""
        self.users.update_one(
            {"user_id": user_id},
            {"$addToSet": {"profile.hobbies": hobby}}
        )
        print(f"📝 {hobby}를 좋아하시는군요! 기억할게요!")
    
    # === 대화 기록 관리 ===
    
    def save_conversation(
        self, 
        user_id: str, 
        user_message: str, 
        emay_response: str,
        emotion: str = "중립"
    ):
        """대화 저장"""
        conversation = {
            "user_id": user_id,
            "timestamp": datetime.now(),
            "user_message": user_message,
            "emay_response": emay_response,
            "emotion_detected": emotion,
            "platform": self.get_user(user_id).get("platform", "unknown")
        }
        
        self.conversations.insert_one(conversation)
        
        # 통계 업데이트
        self.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "stats.conversation_count": 1,
                    "stats.total_messages": 1
                },
                "$set": {"last_interaction": datetime.now()}
            }
        )
        
        # 감정 히스토리 업데이트
        self.users.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "emotional_state.history": {
                        "$each": [{
                            "emotion": emotion,
                            "timestamp": datetime.now()
                        }],
                        "$slice": -10  # 최근 10개만 유지
                    }
                },
                "$set": {"emotional_state.current": emotion}
            }
        )
    
    def get_conversation_history(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """최근 대화 기록 조회"""
        conversations = self.conversations.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return list(conversations)
    
    def get_conversation_context(self, user_id: str, limit: int = 5) -> str:
        """대화 맥락을 텍스트로 반환 (LLM에게 전달용)"""
        history = self.get_conversation_history(user_id, limit)
        
        if not history:
            return "이전 대화 없음"
        
        context = "최근 대화:\n"
        for conv in reversed(history):  # 시간순으로 정렬
            context += f"사용자: {conv['user_message']}\n"
            context += f"이메이: {conv['emay_response']}\n\n"
        
        return context
    
    # === 중요 정보 기억 ===
    
    def remember_important_info(
        self, 
        user_id: str, 
        key: str, 
        value: str,
        category: str = "general"
    ):
        """중요한 정보 저장 (이름, 생일, 좋아하는 것 등)"""
        memory = {
            "user_id": user_id,
            "key": key,
            "value": value,
            "category": category,
            "created_at": datetime.now(),
            "importance": "high"
        }
        
        # 중복 확인 후 업데이트 또는 삽입
        self.memories.update_one(
            {"user_id": user_id, "key": key},
            {"$set": memory},
            upsert=True
        )
        
        print(f"🧠 기억했어요: {key} = {value}")
    
    def recall_memory(self, user_id: str, key: str) -> Optional[str]:
        """특정 기억 불러오기"""
        memory = self.memories.find_one({"user_id": user_id, "key": key})
        return memory["value"] if memory else None
    
    def get_all_memories(self, user_id: str) -> List[Dict]:
        """사용자의 모든 기억 조회"""
        return list(self.memories.find({"user_id": user_id}))
    
    # === 통계 및 분석 ===
    
    def get_user_stats(self, user_id: str) -> Dict:
        """사용자 통계 조회"""
        user = self.get_user(user_id)
        if not user:
            return {}
        
        return {
            "이름": user["name"],
            "가입일": user["joined_at"].strftime("%Y-%m-%d"),
            "마지막 대화": user["last_interaction"].strftime("%Y-%m-%d %H:%M"),
            "총 대화 수": user["stats"]["conversation_count"],
            "총 메시지 수": user["stats"]["total_messages"],
            "현재 감정": user["emotional_state"]["current"]
        }
    
    def close(self):
        """연결 종료"""
        self.client.close()
        print("👋 이메이 메모리 시스템 종료")

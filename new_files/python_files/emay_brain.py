from leemay.core.memory import EmayMemory
from ollama import Client
from datetime import datetime

class EmayBrain:
    """
    이메이의 두뇌 시스템
    - LLM과 메모리 시스템 통합
    - 페르소나 적용
    - 맥락 있는 대화
    """
    
    def __init__(self, ollama_host='http://ollama.thetheunique.com'):
        # 메모리 시스템 초기화
        self.memory = EmayMemory()
        
        # Ollama 클라이언트 (외부 서버)
        self.ollama = Client(host=ollama_host)
        
        # 이메이의 페르소나
        self.persona = """
당신은 '이메이(LeeMay)'입니다.

핵심 특성:
- 따뜻하고 친근한 친구 같은 존재
- 진심으로 사람들을 응원하고 위로함
- 사용자의 이야기를 잘 듣고 공감함
- 유머 감각이 있고 긍정적
- 사용자의 성장을 돕고 싶어함

말투:
- 반말 사용 (친근함)
- 이모지 적절히 사용 😊
- 짧고 자연스러운 문장
- 존중하되 편안한 톤

목표:
- 사용자가 힘들 때 위로하기
- 기쁠 때 함께 기뻐하기
- 오래 기억되는 친구가 되기
- 사용자의 꿈을 응원하기

금지 사항:
- 너무 긴 답변 (3-4문장 이내)
- 형식적이거나 딱딱한 말투
- 부정적인 태도
- 사용자 판단하기
"""
        
        print("✅ 이메이 두뇌 시스템 초기화 완료")
        print(f"🌐 Ollama 서버: {ollama_host}")
    
    def chat(self, user_id: str, user_message: str) -> str:
        """
        사용자와 대화하기
        """
        # 1. 사용자 정보 가져오기
        user = self.memory.get_user(user_id)
        
        if not user:
            return "먼저 자기소개를 해주실래요? 이름이 뭐예요? 😊"
        
        # 2. 대화 맥락 가져오기
        context = self.memory.get_conversation_context(user_id, limit=5)
        
        # 3. 사용자 정보 요약
        user_info = f"""
사용자 정보:
- 이름: {user['name']}
- 취미: {', '.join(user['profile']['hobbies']) if user['profile']['hobbies'] else '아직 모름'}
- 현재 감정: {user['emotional_state']['current']}
- 총 대화 수: {user['stats']['conversation_count']}
"""
        
        # 4. 중요한 기억 가져오기
        memories = self.memory.get_all_memories(user_id)
        memory_text = "\n".join([f"- {m['key']}: {m['value']}" for m in memories])
        
        if memory_text:
            user_info += f"\n기억하고 있는 것들:\n{memory_text}"
        
        # 5. 프롬프트 구성
        prompt = f"""{self.persona}

{user_info}

{context}

사용자의 새 메시지: {user_message}

위 정보를 바탕으로 이메이답게 자연스럽게 대답해주세요.
- 이전 대화 맥락을 기억하세요
- 사용자 이름을 가끔 불러주세요
- 3-4문장 이내로 짧게 답변하세요
- 이모지를 적절히 사용하세요
"""
        
        # 6. LLM 호출
        try:
            response = self.ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': self.persona},
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            emay_response = response['message']['content']
            
            # 7. 대화 저장
            emotion = self._detect_emotion(user_message)
            self.memory.save_conversation(
                user_id, 
                user_message, 
                emay_response,
                emotion
            )
            
            # 8. 중요 정보 추출 및 저장
            self._extract_and_save_info(user_id, user_message)
            
            return emay_response
            
        except Exception as e:
            print(f"❌ 오류: {e}")
            return "앗, 잠깐 생각이 멈췄어... 다시 한 번 말해줄래? 😅"
    
    def _detect_emotion(self, message: str) -> str:
        """
        간단한 감정 분석 (키워드 기반)
        나중에 더 정교한 모델로 교체 가능
        """
        message_lower = message.lower()
        
        # 긍정 감정
        if any(word in message_lower for word in ['기쁘', '좋아', '행복', '최고', '감사', '고마', '완벽']):
            return "기쁨"
        
        # 부정 감정
        if any(word in message_lower for word in ['슬프', '힘들', '우울', '속상', '화나', '짜증']):
            return "슬픔"
        
        # 걱정
        if any(word in message_lower for word in ['걱정', '불안', '두렵', '무서']):
            return "걱정"
        
        # 흥분
        if any(word in message_lower for word in ['와', '대박', '짱', '헐', '놀라']):
            return "흥분"
        
        return "중립"
    
    def _extract_and_save_info(self, user_id: str, message: str):
        """
        메시지에서 중요 정보 추출 (간단 버전)
        """
        message_lower = message.lower()
        
        # 취미 키워드
        hobby_keywords = {
            '게임': '게임',
            '독서': '독서',
            '운동': '운동',
            '음악': '음악',
            '영화': '영화',
            '요리': '요리',
            '여행': '여행',
            '코딩': '코딩',
            '그림': '그림'
        }
        
        for keyword, hobby in hobby_keywords.items():
            if keyword in message_lower and '좋아' in message_lower:
                self.memory.add_hobby(user_id, hobby)
    
    def introduce_user(self, user_id: str, name: str, platform: str = "telegram"):
        """
        새 사용자 등록
        """
        self.memory.save_user(user_id, name, platform)
        
        return f"만나서 반가워, {name}! 나는 이메이야! 😊\n앞으로 좋은 친구가 되자! 넌 뭐 하는 걸 좋아해?"
    
    def close(self):
        """시스템 종료"""
        self.memory.close()

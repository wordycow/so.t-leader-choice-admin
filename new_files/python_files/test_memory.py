from memory import EmayMemory
import time

print("=" * 60)
print("🧠 이메이 메모리 시스템 테스트")
print("=" * 60)
print()

# 메모리 시스템 초기화
memory = EmayMemory()

# 1. 새 사용자 등록
print("📝 테스트 1: 사용자 등록")
print("-" * 60)
memory.save_user("telegram_12345", "홍길동", "telegram")
print()

# 2. 사용자 정보 조회
print("📝 테스트 2: 사용자 정보 조회")
print("-" * 60)
user = memory.get_user("telegram_12345")
print(f"사용자 이름: {user['name']}")
print(f"플랫폼: {user['platform']}")
print()

# 3. 취미 추가
print("📝 테스트 3: 취미 기억하기")
print("-" * 60)
memory.add_hobby("telegram_12345", "게임")
memory.add_hobby("telegram_12345", "독서")
memory.add_hobby("telegram_12345", "코딩")
print()

# 4. 대화 저장
print("📝 테스트 4: 대화 기록 저장")
print("-" * 60)
conversations = [
    ("안녕! 나는 홍길동이야", "안녕하세요 길동님! 만나서 반가워요! 😊", "기쁨"),
    ("오늘 기분이 별로 안 좋아...", "무슨 일이 있었나요? 저한테 말씀해주세요.", "슬픔"),
    ("회사에서 프로젝트가 잘 안 풀려서...", "힘드셨겠어요. 어떤 부분이 어려우신가요?", "걱정"),
    ("그래도 팀원들이 도와줘서 해결했어!", "다행이에요! 좋은 팀원들이 있어서 정말 좋네요! 🎉", "기쁨")
]

for user_msg, emay_msg, emotion in conversations:
    memory.save_conversation("telegram_12345", user_msg, emay_msg, emotion)
    time.sleep(0.1)  # 시간차 두기

print("✅ 4개의 대화가 저장되었어요!")
print()

# 5. 중요 정보 기억
print("📝 테스트 5: 중요 정보 기억하기")
print("-" * 60)
memory.remember_important_info("telegram_12345", "생일", "1990-05-15", "personal")
memory.remember_important_info("telegram_12345", "직업", "개발자", "personal")
memory.remember_important_info("telegram_12345", "좋아하는_음식", "피자", "preferences")
print()

# 6. 대화 맥락 조회
print("📝 테스트 6: 대화 맥락 조회")
print("-" * 60)
context = memory.get_conversation_context("telegram_12345", limit=3)
print(context)

# 7. 기억 불러오기
print("📝 테스트 7: 기억 불러오기")
print("-" * 60)
birthday = memory.recall_memory("telegram_12345", "생일")
job = memory.recall_memory("telegram_12345", "직업")
print(f"생일: {birthday}")
print(f"직업: {job}")
print()

# 8. 사용자 통계
print("📝 테스트 8: 사용자 통계")
print("-" * 60)
stats = memory.get_user_stats("telegram_12345")
for key, value in stats.items():
    print(f"{key}: {value}")
print()

print("=" * 60)
print("🎉 모든 테스트 완료!")
print("=" * 60)

# 메모리 시스템 종료
memory.close()

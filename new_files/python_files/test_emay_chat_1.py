from emay_brain import EmayBrain

print("=" * 60)
print("💬 이메이와 대화하기")
print("=" * 60)
print()

# 이메이 초기화
emay = EmayBrain()

# 테스트 사용자
user_id = "test_user_001"

# 1. 사용자 소개
print("👤 사용자: 안녕! 나는 김철수야")
response = emay.introduce_user(user_id, "김철수", "telegram")
print(f"🤖 이메이: {response}")
print()

# 2. 대화 시작
conversations = [
    "나는 게임 하는 거 정말 좋아해!",
    "오늘 회사에서 승진했어!",
    "너무 기쁘다 ㅎㅎ",
    "근데 요즘 운동도 시작했거든",
    "건강 관리 해야지"
]

for msg in conversations:
    print(f"👤 사용자: {msg}")
    response = emay.chat(user_id, msg)
    print(f"🤖 이메이: {response}")
    print()

print("=" * 60)
print("✅ 대화 테스트 완료!")
print("=" * 60)

# 종료
emay.close()
from youtube_transcript_api import YouTubeTranscriptApi
from emay_brain import EmayBrain
import re

def extract_video_id(url: str) -> str:
    """유튜브 URL에서 비디오 ID 추출"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def learn_from_youtube(video_url: str, user_id: str = "youtube_learner"):
    """유튜브 영상 학습 및 말투 분석"""
    
    print("=" * 60)
    print("📺 유튜브 영상 학습 시작")
    print("=" * 60)
    print()
    
    # 1. 비디오 ID 추출
    video_id = extract_video_id(video_url)
    if not video_id:
        print("❌ 올바른 유튜브 URL이 아니에요")
        print("예시: https://www.youtube.com/watch?v=abc123")
        return
    
    print(f"✅ 비디오 ID: {video_id}")
    print()
    
    # 2. 이메이 초기화
    emay = EmayBrain()
    
    # 3. 자막 가져오기
    print("📥 자막 다운로드 중...")
    try:
        # 한국어 우선, 없으면 영어
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            language = "한국어"
        except:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            language = "영어"
        
        # 전체 텍스트 결합
        full_text = " ".join([t['text'] for t in transcript])
        
        print(f"✅ 자막 추출 완료! ({language}, {len(full_text)}자)")
        print()
        
        # 4. 말투 분석
        print("🔍 말투 분석 중...")
        
        # 자주 나오는 표현 찾기
        sentences = [t['text'] for t in transcript]
        
        speech_patterns = {
            "반말": ["거든", "~ㅎㅎ", "~야", "~어", "해봐", "좋아"],
            "존댓말": ["~니다", "~세요", "~습니다", "~요"],
            "이모티콘": ["ㅋㅋ", "ㅎㅎ", "ㅠㅠ"],
            "강조": ["진짜", "정말", "완전", "너무", "엄청"]
        }
        
        found_patterns = {}
        for category, patterns in speech_patterns.items():
            count = sum(1 for sent in sentences for p in patterns if p in sent)
            if count > 0:
                found_patterns[category] = count
        
        print("📊 발견된 말투 특징:")
        for category, count in found_patterns.items():
            print(f"   - {category}: {count}회")
        print()
        
        # 5. 이메이에게 내용 요약 요청
        print("🤖 이메이가 영상 내용을 분석하고 있어요...")
        print()
        
        # 처음 2000자만 사용 (너무 길면 시간 오래 걸림)
        summary_prompt = f"""
다음 유튜브 영상의 자막 내용이야:

{full_text[:2000]}

이 영상에 대해:
1. 핵심 주제가 뭐야?
2. 가장 중요한 내용 3가지는?
3. 어떤 말투를 사용하고 있어?

짧게 정리해줘!
"""
        
        response = emay.chat(user_id, summary_prompt)
        
        print("=" * 60)
        print("📋 이메이의 분석 결과")
        print("=" * 60)
        print(response)
        print()
        
        # 6. 메모리에 저장
        print("💾 영상 내용을 메모리에 저장 중...")
        emay.memory.remember_important_info(
            user_id,
            f"youtube_{video_id}",
            full_text[:500],
            category="youtube_learning"
        )
        
        # 말투 정보도 저장
        emay.memory.remember_important_info(
            user_id,
            f"youtube_{video_id}_style",
            str(found_patterns),
            category="speaking_style"
        )
        
        print("✅ 학습 완료!")
        print()
        
        # 7. 학습한 내용으로 대화 테스트
        print("=" * 60)
        print("💬 학습한 내용으로 대화 테스트")
        print("=" * 60)
        
        test_questions = [
            "방금 본 영상 기억해?",
            "주요 내용 다시 한 번만 알려줘",
            "어떤 말투였어?"
        ]
        
        for question in test_questions:
            print(f"👤 질문: {question}")
            answer = emay.chat(user_id, question)
            print(f"🤖 이메이: {answer}")
            print()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print()
        print("가능한 원인:")
        print("1. 자막이 없는 영상")
        print("2. 비공개 영상")
        print("3. 연령 제한 영상")
        print("4. 네트워크 오류")
    
    finally:
        emay.close()
        print()
        print("=" * 60)
        print("👋 학습 세션 종료")
        print("=" * 60)

# 메인 실행
if __name__ == "__main__":
    print()
    print("🎬 이메이 유튜브 학습 시스템")
    print()
    
    # 사용자 입력
    video_url = input("📺 유튜브 URL 입력: ").strip()
    
    if video_url:
        learn_from_youtube(video_url)
    else:
        print("❌ URL을 입력하지 않았어요")

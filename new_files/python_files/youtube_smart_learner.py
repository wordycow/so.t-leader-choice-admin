import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from emay_brain import EmayBrain

# Whisper는 필요할 때만 import (설치 안 돼있어도 자막은 작동)
try:
    import whisper
    from pytube import YouTube
    WHISPER_AVAILABLE = True
    print("✅ Whisper 사용 가능")
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper 미설치 (자막 있는 영상만 가능)")

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

def get_subtitle(video_id: str):
    """자막 가져오기 (방법 1)"""
    
    print("📥 자막 확인 중...")
    
    try:
        # 한국어 자막 시도
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            language = "한국어"
        except:
            # 영어 자막 시도
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            language = "영어"
        
        # 전체 텍스트 결합
        full_text = " ".join([t['text'] for t in transcript])
        
        print(f"✅ 자막 발견! ({language}, {len(full_text)}자)")
        
        return {
            "success": True,
            "method": "subtitle",
            "text": full_text,
            "language": language
        }
        
    except Exception as e:
        print(f"❌ 자막 없음: {e}")
        return {"success": False}

def get_audio_transcription(video_url: str):
    """음성→텍스트 변환 (방법 2 - Whisper)"""
    
    if not WHISPER_AVAILABLE:
        return {
            "success": False,
            "error": "Whisper 미설치. pip install openai-whisper 실행 필요"
        }
    
    print()
    print("🎤 자막이 없어서 Whisper로 음성 인식 시작...")
    print("⏳ 시간이 걸립니다 (10분 영상 = 2-3분)")
    print()
    
    audio_path = "temp_audio.mp4"
    
    try:
        # 1. 오디오 다운로드
        print("📥 영상 다운로드 중...")
        yt = YouTube(video_url)
        
        print(f"📺 제목: {yt.title}")
        print(f"⏱️  길이: {yt.length // 60}분 {yt.length % 60}초")
        
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(filename=audio_path)
        
        print("✅ 다운로드 완료!")
        
        # 2. Whisper 음성 인식
        print()
        print("🧠 Whisper 모델 로딩...")
        model = whisper.load_model("base")  # base = 빠름, medium = 정확, large = 느림
        
        print("🔍 음성 분석 중...")
        result = model.transcribe(audio_path, language="ko", verbose=False)
        
        text = result["text"]
        
        print(f"✅ 음성 인식 완료! ({len(text)}자)")
        
        # 3. 임시 파일 삭제
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "success": True,
            "method": "whisper",
            "text": text,
            "title": yt.title
        }
        
    except Exception as e:
        print(f"❌ Whisper 실패: {e}")
        
        # 임시 파일 삭제
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {"success": False, "error": str(e)}

def analyze_speaking_style(text: str):
    """말투 분석"""
    
    speech_patterns = {
        "반말": ["거든", "~야", "~어", "해봐", "좋아", "싫어"],
        "존댓말": ["~니다", "~세요", "~습니다", "~요"],
        "이모티콘": ["ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㄷㄷ"],
        "강조": ["진짜", "정말", "완전", "너무", "엄청", "대박"],
        "친근함": ["~거든요", "~잖아", "있잖아"]
    }
    
    found_patterns = {}
    
    for category, patterns in speech_patterns.items():
        count = sum(text.count(p) for p in patterns)
        if count > 0:
            found_patterns[category] = count
    
    return found_patterns

def smart_learn(video_url: str, user_id: str = "smart_learner"):
    """스마트 학습: 자막 우선, 없으면 Whisper"""
    
    print("=" * 70)
    print("🎓 스마트 유튜브 학습 시스템")
    print("=" * 70)
    print()
    
    # 1. 비디오 ID 추출
    video_id = extract_video_id(video_url)
    if not video_id:
        print("❌ 올바른 유튜브 URL이 아니에요")
        return
    
    print(f"✅ 비디오 ID: {video_id}")
    print()
    
    # 2. 자막 시도
    subtitle_result = get_subtitle(video_id)
    
    if subtitle_result["success"]:
        # 자막 성공
        text = subtitle_result["text"]
        method = "자막"
        title = f"Video_{video_id}"
    else:
        # 자막 실패 → Whisper 시도
        print()
        print("🔄 자막이 없어서 Whisper 사용으로 전환...")
        
        whisper_result = get_audio_transcription(video_url)
        
        if not whisper_result["success"]:
            print()
            print("❌ 학습 실패: 자막도 없고 Whisper도 안 됨")
            print()
            print("해결 방법:")
            print("1. Whisper 설치: pip install openai-whisper pytube")
            print("2. FFmpeg 설치: winget install ffmpeg")
            return
        
        text = whisper_result["text"]
        method = "Whisper 음성 인식"
        title = whisper_result.get("title", f"Video_{video_id}")
    
    print()
    print("=" * 70)
    print(f"📊 학습 방법: {method}")
    print("=" * 70)
    print()
    
    # 3. 텍스트 미리보기
    print(f"📝 추출된 텍스트 ({len(text)}자):")
    print("-" * 70)
    print(text[:300] + "..." if len(text) > 300 else text)
    print("-" * 70)
    print()
    
    # 4. 말투 분석
    print("🔍 말투 분석 중...")
    style_info = analyze_speaking_style(text)
    
    if style_info:
        print("📊 발견된 말투 특징:")
        for category, count in sorted(style_info.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {category}: {count}회")
    else:
        print("   특별한 말투 특징을 찾지 못했어요")
    
    print()
    
    # 5. 이메이 분석
    emay = EmayBrain()
    
    print("🤖 이메이가 영상 내용을 분석하고 있어요...")
    print()
    
    analysis_prompt = f"""
다음 유튜브 영상의 내용이야:

제목: {title}

내용:
{text[:2000]}

이 영상에 대해:
1. 핵심 주제가 뭐야?
2. 가장 중요한 내용 3가지는?
3. 어떤 말투를 사용하고 있어?
4. 인상 깊은 부분은?

간단하게 정리해줘!
"""
    
    response = emay.chat(user_id, analysis_prompt)
    
    print("=" * 70)
    print("📋 이메이의 분석 결과")
    print("=" * 70)
    print(response)
    print()
    
    # 6. 메모리에 저장
    print("💾 학습 내용을 메모리에 저장 중...")
    
    # 영상 내용 저장
    emay.memory.remember_important_info(
        user_id,
        f"youtube_{video_id}_content",
        text[:500],
        category="youtube_learning"
    )
    
    # 말투 정보 저장
    if style_info:
        emay.memory.remember_important_info(
            user_id,
            f"youtube_{video_id}_style",
            str(style_info),
            category="speaking_style"
        )
    
    print("✅ 저장 완료!")
    print()
    
    # 7. 학습 테스트
    print("=" * 70)
    print("💬 학습 확인 테스트")
    print("=" * 70)
    print()
    
    test_questions = [
        "방금 본 영상 기억해?",
        "핵심 내용이 뭐였어?",
        "어떤 말투를 사용했어?"
    ]
    
    for question in test_questions:
        print(f"👤 질문: {question}")
        answer = emay.chat(user_id, question)
        print(f"🤖 이메이: {answer}")
        print()
    
    emay.close()
    
    print("=" * 70)
    print("✅ 학습 완료!")
    print(f"📊 사용 방법: {method}")
    print("=" * 70)

# 메인 실행
if __name__ == "__main__":
    print()
    print("🎓 이메이 스마트 유튜브 학습 시스템")
    print()
    print("특징:")
    print("✅ 자막 있으면 → 자막 사용 (빠름)")
    print("✅ 자막 없으면 → Whisper 음성 인식 (느림)")
    print()
    
    video_url = input("📺 유튜브 URL 입력: ").strip()
    
    if video_url:
        print()
        smart_learn(video_url)
    else:
        print("❌ URL을 입력하지 않았어요")

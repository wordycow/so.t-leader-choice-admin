# -*- coding: utf-8 -*-
"""
Emay 감정 매핑 모듈 (경로 수정 버전)
사용자 메시지에서 감정을 감지하고 해당 이미지 경로를 반환합니다.
"""

import os
import re

# 36개 감정 키워드 매핑 (9개씩 4카테고리)
EMOTION_KEYWORDS = {
    # 기본 감정 (9개)
    "neutral": ["평온", "보통", "그냥", "음", "흠"],
    "happy": ["행복", "기쁜", "좋아", "웃", "신난", "즐거", "굿"],
    "sad": ["슬픈", "우울", "눈물", "서러", "슬프"],
    "worried": ["걱정", "불안", "염려", "조마조마"],
    "excited": ["신나", "두근두근", "설레", "기대", "와"],
    "thinking": ["생각", "고민", "음", "흠"],
    "surprised": ["놀란", "깜짝", "헉", "어머", "오"],
    "calm": ["침착", "차분", "평온", "고요"],
    "focused": ["집중", "몰두", "열심", "진중"],
    
    # 긍정 감정 (9개)
    "confident": ["자신감", "확신", "자신있", "당당"],
    "proud": ["자랑", "뿌듯", "자부", "대견"],
    "grateful": ["감사", "고마", "고맙"],
    "loving": ["사랑", "애정", "좋아해", "러브"],
    "hopeful": ["희망", "기대", "바라", "소망"],
    "relaxed": ["편안", "여유", "릴랙스", "휴식"],
    "playful": ["장난", "재미", "신나", "까불"],
    "motivated": ["동기", "의욕", "열정", "파이팅"],
    "cheerful": ["명랑", "발랄", "밝", "활기"],
    
    # 부정 감정 (9개)
    "angry": ["화", "짜증", "분노", "열받", "빡쳐"],
    "annoyed": ["짜증", "귀찮", "성가", "짜증나"],
    "tired": ["피곤", "지쳐", "힘들", "녹초", "탈진"],
    "disappointed": ["실망", "아쉬", "허탈"],
    "scared": ["무서", "두려", "겁", "공포"],
    "stressed": ["스트레스", "압박", "긴장", "부담"],
    "frustrated": ["좌절", "막막", "답답"],
    "lonely": ["외로", "쓸쓸", "고독"],
    "skeptical": ["회의", "의심", "불신", "진짜?"],
    
    # 상황별 감정 (9개)
    "encouraging": ["격려", "응원", "힘내", "파이팅", "화이팅"],
    "comforting": ["위로", "괜찮", "달래"],
    "apologizing": ["미안", "죄송", "사과"],
    "empathetic": ["공감", "이해", "그러게", "맞아"],
    "curious": ["궁금", "뭐", "어떻게", "왜"],
    "serious": ["진지", "심각", "중요"],
    "listening": ["경청", "듣", "들어줘", "말해봐"],
    "explaining": ["설명", "알려줘", "가르쳐줘"],
    "interested": ["관심", "흥미", "재밌", "신기"]
}

# ⭐ 이미지 기본 경로 (절대 경로로 수정)
IMAGE_BASE_PATH = r"C:\emay_project\emay\images\emotions_36"

def detect_emotion(message):
    """
    메시지에서 감정을 감지합니다.
    
    Args:
        message (str): 사용자 메시지
        
    Returns:
        str: 감지된 감정 키 (예: "happy", "sad", "neutral")
    """
    message_lower = message.lower()
    
    # 키워드 매칭 점수 계산
    emotion_scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in message_lower:
                score += 1
        if score > 0:
            emotion_scores[emotion] = score
    
    # 가장 높은 점수의 감정 반환
    if emotion_scores:
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        return best_emotion
    
    # 매칭되지 않으면 neutral 반환
    return "neutral"

def get_emotion_image_path(emotion):
    """
    감정에 해당하는 이미지 파일 경로를 반환합니다.
    
    Args:
        emotion (str): 감정 키
        
    Returns:
        str: 이미지 파일 절대 경로
    """
    image_filename = f"{emotion}.png"
    image_path = os.path.join(IMAGE_BASE_PATH, image_filename)
    
    # 디버깅: 경로 출력
    print(f"🔍 이미지 경로 요청: {emotion} → {image_path}")
    
    # 파일이 존재하지 않으면 neutral 이미지 반환
    if not os.path.exists(image_path):
        print(f"⚠️  이미지 파일 없음: {image_path}")
        image_path = os.path.join(IMAGE_BASE_PATH, "neutral.png")
        if not os.path.exists(image_path):
            print(f"❌ neutral.png도 없음!")
    else:
        print(f"✅ 이미지 파일 발견!")
    
    return image_path

# 테스트용
if __name__ == "__main__":
    # 경로 확인
    print(f"📂 이미지 폴더: {IMAGE_BASE_PATH}")
    print(f"📂 폴더 존재 여부: {os.path.exists(IMAGE_BASE_PATH)}")
    
    if os.path.exists(IMAGE_BASE_PATH):
        files = os.listdir(IMAGE_BASE_PATH)
        print(f"📋 파일 개수: {len(files)}개")
        print(f"📋 샘플 파일: {files[:5]}")
    
    test_messages = [
        "너무 행복해!",
        "화가 나네...",
        "궁금한데?",
        "피곤해 죽겠어"
    ]
    
    for msg in test_messages:
        emotion = detect_emotion(msg)
        image_path = get_emotion_image_path(emotion)
        print(f"메시지: '{msg}' → 감정: {emotion} → 이미지: {image_path}")

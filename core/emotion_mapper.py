# -*- coding: utf-8 -*-
"""
Emotion Engine (canonical)
- 36개 실물 이미지 키워드 완벽 매핑
- 이미지 경로: C:\leemay_project\leemay\images\<emotion>.png
"""

from __future__ import annotations
from pathlib import Path

# 아빠가 제공한 36개 실물 파일명 기준 완벽 튜닝
EMOTION_KEYWORDS: dict[str, list[str]] = {
    "neutral": [],  # 기본 상태
    "comforting": ["위로", "토닥", "괜찮아", "기운내"],
    "confident": ["자신", "확신", "당당", "할수있어"],
    "curious": ["궁금", "신기", "호기심", "알려줘", "왜"],
    "disappointed": ["실망", "아쉽", "허탈", "쩝"],
    "empathetic": ["공감", "이해", "맞아", "그렇구나"],
    "encouraging": ["응원", "파이팅", "화이팅", "잘할거야"],
    "excited": ["신나", "흥분", "기대", "두근", "야호"],
    "explaining": ["설명", "알려줄게", "정리하자면", "말하자면"],
    "focused": ["집중", "몰입", "진지하게"],
    "frustrated": ["답답", "환장", "미치겠", "어휴"],
    "grateful": ["감사", "고마워", "땡큐", "은혜"],
    "happy": ["좋아", "행복", "굿", "ㅋㅋ", "ㅎㅎ"],
    "hopeful": ["희망", "바래", "잘될거야"],
    "interested": ["흥미", "재미", "솔깃", "오호"],
    "listening": ["듣고", "말해봐", "어디한번"],
    "lonely": ["외로", "고독", "쓸쓸", "혼자"],
    "loving": ["사랑", "애정", "하트", "알라뷰"],
    "motivated": ["동기", "자극", "의욕", "열정"],
    "playful": ["장난", "농담", "메롱", "까꿍"],
    "proud": ["자랑", "뿌듯", "자부심", "대견"],
    "relaxed": ["편안", "평온", "나른", "여유", "힐링"],
    "sad": ["슬퍼", "우울", "눈물", "흑흑", "ㅠㅠ"],
    "scared": ["무서", "두려", "겁나", "오싹", "ㄷㄷ"],
    "serious": ["심각", "진지해", "장난아냐"],
    "skeptical": ["의심", "글쎄", "과연", "정말일까"],
    "stressed": ["스트레스", "압박", "터질것같", "미치겠네"],
    "surprised": ["놀람", "깜짝", "헐", "대박", "헉"],
    "thinking": ["고민", "생각해", "음...", "어쩌지"],
    "tired": ["피곤", "지쳐", "졸려", "기진맥진", "뻗었"],
    "worried": ["걱정", "불안", "우려", "어떡해"],
    "angry": ["화나", "열받", "분노", "빡치", "씨발"],
    "annoyed": ["짜증", "귀찮", "성가신", "아놔"],
    "apologizing": ["미안", "죄송", "사과", "내잘못"],
    "calm": ["침착", "진정", "차분"],
    "cheerful": ["쾌활", "발랄", "기운차", "룰루"]
}

def detect_emotion(msg: str) -> str:
    t = (msg or "").strip().lower()
    if not t:
        return "neutral"

    for emo, kws in EMOTION_KEYWORDS.items():
        for k in kws:
            if k.lower() in t:
                return emo
    return "neutral"

def get_emotion_image_path(base_dir: Path, emotion: str) -> str:
    """
    base_dir: C:\\leemay_project (프로젝트 루트)
    images:    base_dir\\leemay\\images\\<emotion>.png
    """
    # 아빠의 실제 폴더 경로(leemay\images)로 완벽 매핑
    emotions_dir = base_dir / "leemay" / "images"
    p = emotions_dir / f"{emotion}.png"
    if p.exists():
        return str(p)
    
    # 만약 파일이 없으면 무표정(neutral)으로 안전하게 방어
    fallback = emotions_dir / "neutral.png"
    return str(fallback) if fallback.exists() else ""
# C:\emay_project\generate_emotions.py

import google.generativeai as genai
import os
import time
import base64

# Gemini API 설정
GEMINI_API_KEY = "AIzaSyBdki04bcXZXh3xzY0VDLRQ1ZDqwMNlAUY"
genai.configure(api_key=GEMINI_API_KEY)

# 모델 설정
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 이미지 저장 폴더
output_dir = "emay/images"
os.makedirs(output_dir, exist_ok=True)

# 36가지 감정 정의
emotions = {
    # 기본 6종
    "neutral": "calm, professional, neutral expression, slight smile",
    "happy": "bright cheerful smile, joyful eyes, very happy",
    "sad": "sad gentle expression, comforting eyes, empathetic",
    "worried": "concerned worried expression, slightly furrowed brows",
    "excited": "very excited, wide eyes, enthusiastic big smile",
    "thinking": "thoughtful, hand near chin, concentrated focused",
    
    # 긍정 10종
    "confident": "strong confident posture, determined eyes, assured",
    "proud": "satisfied proud smile, accomplished look",
    "grateful": "warm thankful smile, appreciative eyes",
    "loving": "affectionate warm expression, kind loving eyes",
    "hopeful": "optimistic bright eyes, hopeful smile",
    "relaxed": "peaceful relaxed expression, calm comfortable",
    "playful": "cute playful smile, fun winking expression",
    "motivated": "energetic determined look, motivated expression",
    "satisfied": "content pleased smile, satisfied look",
    "touched": "moved emotional expression, touched teary eyes",
    
    # 부정 10종
    "angry": "frustrated angry expression, stern look",
    "annoyed": "slightly irritated annoyed expression",
    "tired": "exhausted weary eyes, tired expression",
    "disappointed": "disappointed sad eyes, let down",
    "scared": "frightened worried scared look",
    "stressed": "tense anxious stressed expression",
    "frustrated": "frustrated defeated look, upset",
    "jealous": "envious jealous sideways glance",
    "guilty": "regretful apologetic guilty look",
    "lonely": "isolated lonely melancholic expression",
    
    # 상황별 10종
    "encouraging": "supportive warm encouraging smile, nodding",
    "comforting": "gentle reassuring comforting expression",
    "celebrating": "joyful celebratory excited smile",
    "apologizing": "sincere apologetic sorry expression",
    "empathetic": "understanding compassionate empathetic look",
    "surprised": "shocked surprised wide-eyed expression",
    "curious": "inquisitive curious raised eyebrows",
    "serious": "focused serious professional demeanor",
    "listening": "attentive engaged listening expression",
    "explaining": "clear instructive explaining look"
}

# 기본 프롬프트
base_prompt = """
Create a professional portrait photograph:

Subject: Korean woman in late 20s
Face: Round face, smooth skin, natural makeup
Hairstyle: Short bob haircut, dark brown hair with slight wave
Outfit: Navy blue blazer, white collared shirt, small pearl earrings
Background: Clean light gray studio background
Lighting: Soft professional studio lighting, even illumination
Camera: Front-facing portrait, shoulders and face visible
Quality: High-resolution, sharp focus, professional photography

Expression: {expression}

IMPORTANT: Keep the same person's face features, hairstyle, and outfit consistent. Only change the facial expression.
"""

print("🎨 이메이 감정 이미지 36종 생성 시작...")
print("=" * 70)
print(f"저장 위치: {os.path.abspath(output_dir)}")
print("=" * 70)

success_count = 0
failed_list = []

for i, (emotion_name, expression) in enumerate(emotions.items(), 1):
    print(f"\n[{i}/36] {emotion_name} 생성 중...")
    
    prompt = base_prompt.format(expression=expression)
    
    try:
        # Gemini로 이미지 생성
        response = model.generate_content(
            [prompt],
            generation_config=genai.GenerationConfig(
                temperature=0.4,
            )
        )
        
        # 응답 확인
        if response.candidates:
            for part in response.candidates[0].content.parts:
                # 이미지 데이터 확인
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    
                    # 이미지 저장
                    image_path = os.path.join(output_dir, f"{emotion_name}.png")
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"✅ {emotion_name}.png 저장 완료!")
                    success_count += 1
                    break
            else:
                print(f"⚠️ {emotion_name}: 이미지 데이터 없음")
                failed_list.append(emotion_name)
        else:
            print(f"⚠️ {emotion_name}: 응답 없음")
            failed_list.append(emotion_name)
        
        # API 제한 방지
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ {emotion_name} 실패: {e}")
        failed_list.append(emotion_name)
        time.sleep(3)

print("\n" + "=" * 70)
print(f"🎉 생성 완료!")
print(f"✅ 성공: {success_count}/36")
if failed_list:
    print(f"❌ 실패: {len(failed_list)}개")
    print(f"   {', '.join(failed_list)}")
print(f"📂 저장 위치: {os.path.abspath(output_dir)}")
print("=" * 70)

# 생성된 이미지 확인
if success_count > 0:
    print("\n📋 생성된 이미지:")
    images = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
    for img in images:
        print(f"  - {img}")

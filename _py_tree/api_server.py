# -*- coding: utf-8 -*-
"""
🤖 Lee May Training Center - 완전 통합 API 서버
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4대 핵심 모듈 유기적 통합:
1. 🎭 Emotion Engine (페르소나-감정-이미지 삼위일체)
2. 📚 Knowledge RAG (유튜브 자막 추출 및 LLM 주입)
3. 📊 Live Telemetry (실시간 시스템/트레이딩 데이터)
4. 🔗 Central Command (모든 봇 중앙 관리)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import psutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# 🔧 경로 설정
# ============================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
STATIC_DIR = os.path.join(WEB_DIR, 'static')
LEEMAY_DIR = os.path.join(BASE_DIR, 'leemay')
IMAGES_DIR = os.path.join(LEEMAY_DIR, 'images')
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'knowledge_base')
PERSONAS_DIR = os.path.join(LEEMAY_DIR, 'personas')

# 폴더 생성
for folder in [KNOWLEDGE_DIR, PERSONAS_DIR, IMAGES_DIR]:
    os.makedirs(folder, exist_ok=True)

# 모듈 경로 추가
sys.path.append(BASE_DIR)
sys.path.append(LEEMAY_DIR)
sys.path.append(os.path.join(LEEMAY_DIR, 'core'))

# ============================================================
# 📦 모듈 임포트
# ============================================================
try:
    from leemay.core.emay_brain import EmayBrain
    from leemay.core.memory import EmayMemory
    from emotion_mapper import detect_emotion, get_emotion_image_path, EMOTION_KEYWORDS
    EMAY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Emay 모듈 로드 실패: {e}")
    EMAY_AVAILABLE = False

# YouTube 자막 추출
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    import re
    YOUTUBE_AVAILABLE = True
except ImportError:
    print("⚠️  youtube_transcript_api 없음 - pip install youtube-transcript-api")
    YOUTUBE_AVAILABLE = False

# ============================================================
# 🌐 Flask 앱 초기화
# ============================================================
app = Flask(__name__, 
            static_folder=STATIC_DIR, 
            template_folder=WEB_DIR)

# CORS 완전 개방
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """OPTIONS 요청 처리"""
    response = jsonify({"status": "ok"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ============================================================
# 🎭 1. EMOTION ENGINE - 페르소나/감정/이미지 시스템
# ============================================================
class EmotionEngine:
    """감정 기반 이미지 및 페르소나 관리"""
    
    def __init__(self):
        self.personas = {}
        self.current_emotion = "neutral"
        self.emotion_history = []
        self.load_personas()
        
    def load_personas(self):
        """페르소나 파일 로드"""
        persona_file = os.path.join(PERSONAS_DIR, 'emay_persona.json')
        
        if os.path.exists(persona_file):
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    self.personas = json.load(f)
                print(f"✅ 페르소나 로드 완료: {len(self.personas)}개")
            except Exception as e:
                print(f"⚠️  페르소나 로드 실패: {e}")
                self._create_default_persona()
        else:
            self._create_default_persona()
    
    def _create_default_persona(self):
        """기본 페르소나 생성"""
        self.personas = {
            "default": {
                "name": "Lee May",
                "personality": "친근하고 따뜻한 친구",
                "tone": "반말, 이모지 사용",
                "traits": ["공감능력", "긍정적", "유머러스"]
            }
        }
        
        # 파일 저장
        persona_file = os.path.join(PERSONAS_DIR, 'emay_persona.json')
        with open(persona_file, 'w', encoding='utf-8') as f:
            json.dump(self.personas, f, ensure_ascii=False, indent=2)
        print("✅ 기본 페르소나 생성 완료")
    
    def analyze_emotion(self, message: str) -> dict:
        """메시지에서 감정 분석"""
        emotion = detect_emotion(message)
        self.current_emotion = emotion
        self.emotion_history.append({
            "emotion": emotion,
            "timestamp": datetime.now().isoformat(),
            "message": message[:50]
        })
        
        # 최근 10개만 유지
        if len(self.emotion_history) > 10:
            self.emotion_history = self.emotion_history[-10:]
        
        return {
            "emotion": emotion,
            "image_path": f"/image/{emotion}",
            "confidence": self._calculate_confidence(message, emotion)
        }
    
    def _calculate_confidence(self, message: str, emotion: str) -> float:
        """감정 신뢰도 계산"""
        keywords = EMOTION_KEYWORDS.get(emotion, [])
        matches = sum(1 for kw in keywords if kw in message.lower())
        return min(matches / max(len(keywords), 1), 1.0) * 100

# ============================================================
# 📚 2. KNOWLEDGE RAG - 유튜브 학습 시스템
# ============================================================
class KnowledgeRAG:
    """유튜브 자막 추출 및 지식 저장"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """저장된 지식 로드"""
        kb_file = os.path.join(KNOWLEDGE_DIR, 'knowledge_base.json')
        
        if os.path.exists(kb_file):
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                print(f"✅ 지식 베이스 로드: {len(self.knowledge_base)}개")
            except Exception as e:
                print(f"⚠️  지식 베이스 로드 실패: {e}")
    
    def save_knowledge(self):
        """지식 베이스 저장"""
        kb_file = os.path.join(KNOWLEDGE_DIR, 'knowledge_base.json')
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def extract_youtube_id(self, url: str) -> str:
        """유튜브 URL에서 비디오 ID 추출"""
        if not YOUTUBE_AVAILABLE:
            return None
        
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
    
    def learn_from_youtube(self, url: str) -> dict:
        """유튜브 영상에서 학습"""
        if not YOUTUBE_AVAILABLE:
            return {"success": False, "error": "YouTube API 미설치"}
        
        video_id = self.extract_youtube_id(url)
        if not video_id:
            return {"success": False, "error": "올바른 유튜브 URL이 아닙니다"}
        
        try:
            # 자막 가져오기
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
                language = "한국어"
            except:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                language = "영어"
            
            # 텍스트 결합
            full_text = " ".join([t['text'] for t in transcript])
            
            # 지식 베이스에 저장
            self.knowledge_base[video_id] = {
                "url": url,
                "language": language,
                "text": full_text,
                "length": len(full_text),
                "timestamp": datetime.now().isoformat(),
                "summary": full_text[:500]  # 첫 500자
            }
            
            self.save_knowledge()
            
            return {
                "success": True,
                "video_id": video_id,
                "language": language,
                "length": len(full_text),
                "summary": full_text[:500]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_knowledge(self, query: str) -> list:
        """지식 베이스 검색"""
        results = []
        query_lower = query.lower()
        
        for video_id, data in self.knowledge_base.items():
            if query_lower in data['text'].lower():
                results.append({
                    "video_id": video_id,
                    "url": data['url'],
                    "summary": data['summary'],
                    "timestamp": data['timestamp']
                })
        
        return results

# ============================================================
# 📊 3. LIVE TELEMETRY - 실시간 모니터링
# ============================================================
class LiveTelemetry:
    """실시간 시스템 및 트레이딩 데이터"""
    
    def __init__(self):
        self.trading_data = {
            "balance": 1000000,  # 더미 데이터
            "profit": 0,
            "trades": 0
        }
    
    def get_system_stats(self) -> dict:
        """실시간 시스템 리소스"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": round(cpu_percent, 1),
                "memory": round(memory.percent, 1),
                "disk": round(disk.percent, 1),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_trading_stats(self) -> dict:
        """트레이딩 통계 (더미 데이터)"""
        # TODO: 실제 트레이딩 봇 API 연동
        return {
            "balance": self.trading_data["balance"],
            "profit": self.trading_data["profit"],
            "profit_rate": (self.trading_data["profit"] / self.trading_data["balance"]) * 100,
            "trades_today": self.trading_data["trades"],
            "status": "running"
        }

# ============================================================
# 🔗 4. CENTRAL COMMAND - 봇 관리 시스템
# ============================================================
class CentralCommand:
    """모든 봇의 중앙 관리"""
    
    def __init__(self):
        self.bots = {
            "leemay_api": {"running": True, "pid": os.getpid()},
            "ollama_tunnel": {"running": False, "pid": None},
            "youtube_learner": {"running": False, "pid": None}
        }
    
    def check_bot_status(self, bot_name: str) -> dict:
        """봇 상태 확인"""
        if bot_name == "leemay_api":
            return {"running": True, "pid": os.getpid()}
        
        if bot_name == "ollama_tunnel":
            # cloudflared 프로세스 확인
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'cloudflared' in proc.info['name'].lower():
                        return {"running": True, "pid": proc.info['pid']}
                except:
                    pass
        
        return {"running": False, "pid": None}
    
    def self_diagnose(self) -> dict:
        """자가 진단"""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "health": "healthy"
        }
        
        # 각 모듈 체크
        modules_status = {
            "EmayBrain": EMAY_AVAILABLE,
            "YouTube": YOUTUBE_AVAILABLE,
            "psutil": True,
            "Flask": True
        }
        
        diagnosis["modules"] = modules_status
        
        if not all(modules_status.values()):
            diagnosis["health"] = "degraded"
        
        return diagnosis

# ============================================================
# 🚀 글로벌 인스턴스 생성
# ============================================================
emotion_engine = EmotionEngine()
knowledge_rag = KnowledgeRAG()
live_telemetry = LiveTelemetry()
central_command = CentralCommand()

# Emay Brain (사용 가능하면)
emay_brain = None
if EMAY_AVAILABLE:
    try:
        emay_brain = EmayBrain()
        print("✅ Emay Brain 초기화 완료")
    except Exception as e:
        print(f"⚠️  Emay Brain 초기화 실패: {e}")

# ============================================================
# 🌐 API 라우트
# ============================================================

@app.route('/')
def index():
    """대시보드"""
    dashboard_path = os.path.join(WEB_DIR, 'dashboard.html')
    if os.path.exists(dashboard_path):
        return send_from_directory(WEB_DIR, 'dashboard.html')
    return jsonify({"error": "Dashboard not found"}), 404

@app.route('/health', methods=['GET'])
def health():
    """헬스체크"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "EmayBrain": EMAY_AVAILABLE,
            "YouTube": YOUTUBE_AVAILABLE
        }
    }), 200

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎭 Emotion Engine API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/chat', methods=['POST'])
def chat():
    """채팅 엔드포인트"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'web_user')
        
        if not message:
            return jsonify({"error": "메시지가 필요합니다"}), 400
        
        # 감정 분석
        emotion_result = emotion_engine.analyze_emotion(message)
        
        # Emay 응답 생성
        if emay_brain:
            try:
                response = emay_brain.chat(user_id, message)
            except:
                response = "안녕! 나는 Lee May야! 😊 무엇을 도와줄까?"
        else:
            response = "안녕! 나는 Lee May야! 😊 무엇을 도와줄까?"
        
        return jsonify({
            "response": response,
            "emotion": emotion_result["emotion"],
            "image_url": emotion_result["image_path"],
            "confidence": emotion_result["confidence"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image/<emotion>', methods=['GET'])
def get_emotion_image(emotion):
    """감정 이미지 제공"""
    try:
        image_path = get_emotion_image_path(emotion)
        
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/png')
        else:
            # 이미지 없으면 neutral 반환
            neutral_path = get_emotion_image_path("neutral")
            if os.path.exists(neutral_path):
                return send_file(neutral_path, mimetype='image/png')
            else:
                return jsonify({"error": "Image not found"}), 404
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/emotions', methods=['GET'])
def list_emotions():
    """사용 가능한 감정 목록"""
    emotions = list(EMOTION_KEYWORDS.keys())
    return jsonify({
        "emotions": emotions,
        "count": len(emotions)
    }), 200

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📚 Knowledge RAG API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/learning/youtube', methods=['POST'])
def learn_youtube():
    """유튜브 학습"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"success": False, "error": "URL이 필요합니다"}), 400
        
        result = knowledge_rag.learn_from_youtube(url)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/knowledge/search', methods=['POST'])
def search_knowledge():
    """지식 베이스 검색"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        results = knowledge_rag.search_knowledge(query)
        return jsonify({"results": results, "count": len(results)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/knowledge/list', methods=['GET'])
def list_knowledge():
    """저장된 지식 목록"""
    items = []
    for video_id, data in knowledge_rag.knowledge_base.items():
        items.append({
            "video_id": video_id,
            "url": data['url'],
            "language": data['language'],
            "length": data['length'],
            "timestamp": data['timestamp']
        })
    
    return jsonify({"knowledge": items, "count": len(items)}), 200

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 Live Telemetry API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """실시간 시스템 상태"""
    stats = live_telemetry.get_system_stats()
    return jsonify(stats), 200

@app.route('/api/trading/status', methods=['GET'])
def trading_status():
    """트레이딩 상태"""
    stats = live_telemetry.get_trading_stats()
    return jsonify(stats), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Lee May 능력치"""
    # TODO: 실제 계산 로직
    return jsonify({
        "leemay": {
            "emotion_expression": 85,
            "conversation_understanding": 72,
            "memory": 90,
            "humor": 45,
            "empathy": 68
        }
    }), 200

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔗 Central Command API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/bots/status', methods=['GET'])
def bots_status():
    """모든 봇 상태"""
    status = {}
    
    for bot_name in central_command.bots.keys():
        bot_status = central_command.check_bot_status(bot_name)
        status[bot_name] = bot_status
    
    return jsonify(status), 200

@app.route('/api/system/diagnose', methods=['GET'])
def system_diagnose():
    """시스템 자가 진단"""
    diagnosis = central_command.self_diagnose()
    return jsonify(diagnosis), 200

# ============================================================
# 🚀 서버 시작
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("🤖 LEE MAY TRAINING CENTER - INTEGRATED API SERVER")
    print("=" * 70)
    print()
    print("📍 서버 주소:")
    print(f"   로컬:  http://localhost:5001")
    print(f"   외부:  https://leemay.thetheunique.com")
    print()
    print("🎭 통합 모듈:")
    print(f"   ✅ Emotion Engine (36개 감정)")
    print(f"   {'✅' if YOUTUBE_AVAILABLE else '⚠️ '} Knowledge RAG (유튜브 학습)")
    print(f"   ✅ Live Telemetry (실시간 모니터링)")
    print(f"   ✅ Central Command (봇 관리)")
    print()
    print("🔗 주요 엔드포인트:")
    print(f"   POST /chat - 채팅")
    print(f"   GET  /image/<emotion> - 감정 이미지")
    print(f"   POST /api/learning/youtube - 유튜브 학습")
    print(f"   GET  /api/system/status - 시스템 상태")
    print(f"   GET  /api/bots/status - 봇 상태")
    print(f"   GET  /api/system/diagnose - 자가 진단")
    print()
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True)

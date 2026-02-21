#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 업비트 봇 라이선스 서버
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
이 서버는 라이선스 검증 및 전략 시그니처를 제공합니다.
클라이언트는 매 30분마다 이 서버에 연결하여 라이선스를 확인합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import hmac
import time
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════
# 🔑 보안 설정 (절대 공개하지 마세요!)
# ═══════════════════════════════════════════════════════
SECRET_KEY = "your-super-secret-key-change-this-12345"  # 반드시 변경!
MASTER_PASSWORD = "your-master-password-654321"  # 반드시 변경!

# 라이선스 데이터베이스 (실제로는 PostgreSQL, MongoDB 등 사용 권장)
# 여기서는 JSON 파일로 간단히 구현
LICENSE_DB_FILE = "license_database.json"

# ═══════════════════════════════════════════════════════
# 📊 라이선스 데이터베이스 관리
# ═══════════════════════════════════════════════════════

def load_licenses():
    """라이선스 데이터베이스 로드"""
    if os.path.exists(LICENSE_DB_FILE):
        with open(LICENSE_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_licenses(licenses):
    """라이선스 데이터베이스 저장"""
    with open(LICENSE_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(licenses, f, indent=2, ensure_ascii=False)

# ═══════════════════════════════════════════════════════
# 🔐 보안 함수
# ═══════════════════════════════════════════════════════

def generate_signature(data, secret_key):
    """HMAC 시그니처 생성"""
    message = json.dumps(data, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_signature(data, signature, secret_key):
    """HMAC 시그니처 검증"""
    expected = generate_signature(data, secret_key)
    return hmac.compare_digest(expected, signature)

def generate_machine_id(ip, user_agent):
    """머신 ID 생성 (같은 컴퓨터는 같은 ID)"""
    combined = f"{ip}:{user_agent}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]

# ═══════════════════════════════════════════════════════
# 🌐 API 엔드포인트
# ═══════════════════════════════════════════════════════

@app.route('/api/v1/license/register', methods=['POST'])
def register_license():
    """라이선스 등록 (TXID 확인 후)"""
    try:
        data = request.json
        txid = data.get('txid')
        amount = data.get('amount')
        machine_id = data.get('machine_id')
        master_password = data.get('master_password')
        
        # 마스터 패스워드 확인 (관리자만 등록 가능)
        if master_password != MASTER_PASSWORD:
            return jsonify({
                'success': False,
                'error': 'Invalid master password'
            }), 403
        
        # 라이선스 DB 로드
        licenses = load_licenses()
        
        # 이미 등록된 TXID인지 확인
        if txid in licenses:
            return jsonify({
                'success': False,
                'error': 'TXID already registered'
            }), 400
        
        # 기간 계산 (1 USDT = 1일)
        days = int(amount)  # 소수점 버림
        start_date = datetime.now()
        expiry_date = start_date + timedelta(days=days)
        
        # 라이선스 등록
        licenses[txid] = {
            'txid': txid,
            'amount': amount,
            'days': days,
            'start_date': start_date.isoformat(),
            'expiry_date': expiry_date.isoformat(),
            'machine_id': machine_id,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_verified': None
        }
        
        save_licenses(licenses)
        
        return jsonify({
            'success': True,
            'message': 'License registered successfully',
            'license': licenses[txid]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/license/verify', methods=['POST'])
def verify_license():
    """
    라이선스 검증 (클라이언트가 30분마다 호출)
    
    요청 형식:
    {
        "txid": "...",
        "machine_id": "...",
        "timestamp": 1234567890,
        "signature": "..."
    }
    """
    try:
        data = request.json
        txid = data.get('txid')
        machine_id = data.get('machine_id')
        timestamp = data.get('timestamp')
        signature = data.get('signature')
        
        # 타임스탬프 확인 (5분 이내만 허용)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'Request expired'
            }), 400
        
        # 시그니처 검증
        verify_data = {
            'txid': txid,
            'machine_id': machine_id,
            'timestamp': timestamp
        }
        if not verify_signature(verify_data, signature, SECRET_KEY):
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'Invalid signature'
            }), 403
        
        # 라이선스 DB 로드
        licenses = load_licenses()
        
        # TXID 확인
        if txid not in licenses:
            return jsonify({
                'success': True,
                'valid': False,
                'error': 'License not found'
            })
        
        license_info = licenses[txid]
        
        # 머신 ID 확인 (다른 컴퓨터에서 실행 방지)
        if license_info['machine_id'] != machine_id:
            return jsonify({
                'success': True,
                'valid': False,
                'error': 'License is bound to another machine'
            })
        
        # 만료일 확인
        expiry_date = datetime.fromisoformat(license_info['expiry_date'])
        if datetime.now() > expiry_date:
            license_info['status'] = 'expired'
            save_licenses(licenses)
            return jsonify({
                'success': True,
                'valid': False,
                'error': 'License expired'
            })
        
        # 라이선스 유효!
        license_info['last_verified'] = datetime.now().isoformat()
        save_licenses(licenses)
        
        # 전략 시그니처 생성 (중요!)
        strategy_data = {
            'txid': txid,
            'timestamp': current_time,
            'valid_until': int((expiry_date - datetime.now()).total_seconds())
        }
        strategy_signature = generate_signature(strategy_data, SECRET_KEY)
        
        return jsonify({
            'success': True,
            'valid': True,
            'license': {
                'txid': txid,
                'status': license_info['status'],
                'expiry_date': license_info['expiry_date'],
                'days_left': (expiry_date - datetime.now()).days
            },
            'strategy_signature': strategy_signature,
            'strategy_data': strategy_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'valid': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/license/list', methods=['POST'])
def list_licenses():
    """라이선스 목록 조회 (관리자 전용)"""
    try:
        data = request.json
        master_password = data.get('master_password')
        
        if master_password != MASTER_PASSWORD:
            return jsonify({
                'success': False,
                'error': 'Invalid master password'
            }), 403
        
        licenses = load_licenses()
        
        # 상태 업데이트
        for txid, info in licenses.items():
            expiry_date = datetime.fromisoformat(info['expiry_date'])
            if datetime.now() > expiry_date and info['status'] == 'active':
                info['status'] = 'expired'
        
        save_licenses(licenses)
        
        return jsonify({
            'success': True,
            'licenses': licenses,
            'total': len(licenses),
            'active': sum(1 for l in licenses.values() if l['status'] == 'active')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'ok',
        'server': 'Upbit Bot License Server',
        'version': '1.0',
        'time': datetime.now().isoformat()
    })

# ═══════════════════════════════════════════════════════
# 🚀 서버 실행
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 업비트 봇 라이선스 서버 시작")
    print("=" * 60)
    print()
    print("⚠️  보안 경고:")
    print("  - SECRET_KEY와 MASTER_PASSWORD를 반드시 변경하세요!")
    print("  - 실제 배포 시 HTTPS를 사용하세요!")
    print("  - 프로덕션 환경에서는 PostgreSQL 등 DB 사용 권장")
    print()
    print("📡 API 엔드포인트:")
    print("  - POST /api/v1/license/register  (라이선스 등록)")
    print("  - POST /api/v1/license/verify    (라이선스 검증)")
    print("  - POST /api/v1/license/list      (라이선스 목록)")
    print("  - GET  /api/v1/health            (서버 상태)")
    print()
    print("=" * 60)
    
    # 포트 8000에서 실행 (5000은 봇이 사용)
    app.run(host='0.0.0.0', port=8000, debug=False)

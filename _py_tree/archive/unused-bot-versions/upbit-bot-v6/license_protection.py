#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 라이선스 보호 모듈
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
이 모듈은 라이선스 서버와 통신하여 라이선스를 검증합니다.
30분마다 자동으로 라이선스를 재확인합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import hashlib
import hmac
import time
import json
import requests
from datetime import datetime
import platform
import uuid

# ═══════════════════════════════════════════════════════
# 🔒 보안 설정 (난독화됨)
# ═══════════════════════════════════════════════════════
# 실제 배포 시 PyArmor로 이 파일을 암호화하세요!

LICENSE_SERVER_URL = "https://your-license-server.com/api/v1"  # 내 서버 주소
SECRET_KEY = "your-super-secret-key-change-this-12345"  # 서버와 동일하게

# ═══════════════════════════════════════════════════════
# 🖥️ 머신 ID 생성
# ═══════════════════════════════════════════════════════

def get_machine_id():
    """
    현재 컴퓨터의 고유 ID 생성
    - 같은 컴퓨터는 항상 같은 ID
    - 다른 컴퓨터는 다른 ID
    """
    try:
        # MAC 주소 기반 머신 ID
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                        for elements in range(0,2*6,2)][::-1])
        
        # 시스템 정보 추가
        system_info = f"{platform.system()}:{platform.node()}:{mac}"
        
        # SHA256 해시
        machine_id = hashlib.sha256(system_info.encode()).hexdigest()[:16]
        
        return machine_id
    except:
        # 실패 시 랜덤 ID (보안상 취약하지만 백업)
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]

# ═══════════════════════════════════════════════════════
# 🔐 시그니처 생성
# ═══════════════════════════════════════════════════════

def generate_signature(data, secret_key):
    """HMAC 시그니처 생성 (서버와 동일한 방식)"""
    message = json.dumps(data, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

# ═══════════════════════════════════════════════════════
# 📡 서버 통신
# ═══════════════════════════════════════════════════════

def verify_license_with_server(txid):
    """
    서버에 라이선스 검증 요청
    
    반환값:
    {
        'valid': True/False,
        'error': '오류 메시지' (실패 시),
        'days_left': 남은 일수,
        'strategy_signature': '전략 시그니처'
    }
    """
    try:
        machine_id = get_machine_id()
        timestamp = int(time.time())
        
        # 요청 데이터
        request_data = {
            'txid': txid,
            'machine_id': machine_id,
            'timestamp': timestamp
        }
        
        # 시그니처 생성
        signature = generate_signature(request_data, SECRET_KEY)
        request_data['signature'] = signature
        
        # 서버에 요청
        response = requests.post(
            f"{LICENSE_SERVER_URL}/license/verify",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('valid'):
                return {
                    'valid': True,
                    'days_left': result['license']['days_left'],
                    'expiry_date': result['license']['expiry_date'],
                    'strategy_signature': result['strategy_signature']
                }
            else:
                return {
                    'valid': False,
                    'error': result.get('error', 'Unknown error')
                }
        else:
            return {
                'valid': False,
                'error': f'Server error: {response.status_code}'
            }
            
    except requests.RequestException as e:
        return {
            'valid': False,
            'error': f'Network error: {str(e)}'
        }
    except Exception as e:
        return {
            'valid': False,
            'error': f'Unexpected error: {str(e)}'
        }

# ═══════════════════════════════════════════════════════
# 🔒 라이선스 검증 (메인 함수)
# ═══════════════════════════════════════════════════════

class LicenseValidator:
    """라이선스 검증기"""
    
    def __init__(self):
        self.last_check = 0
        self.check_interval = 1800  # 30분마다 재확인
        self.is_valid = False
        self.days_left = 0
        self.error_message = ""
        
    def validate(self, txid):
        """
        라이선스 검증
        - 30분마다 서버에 재확인
        - 실패 시 즉시 봇 중지
        """
        current_time = time.time()
        
        # 30분마다 재확인
        if current_time - self.last_check < self.check_interval:
            return self.is_valid
        
        # 서버에 검증 요청
        result = verify_license_with_server(txid)
        
        self.last_check = current_time
        self.is_valid = result.get('valid', False)
        self.days_left = result.get('days_left', 0)
        self.error_message = result.get('error', '')
        
        return self.is_valid
    
    def get_status(self):
        """라이선스 상태 반환"""
        return {
            'valid': self.is_valid,
            'days_left': self.days_left,
            'error': self.error_message,
            'last_check': datetime.fromtimestamp(self.last_check).isoformat()
        }

# ═══════════════════════════════════════════════════════
# 🧪 테스트
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    print("🔐 라이선스 보호 모듈 테스트")
    print("=" * 60)
    print()
    
    print(f"🖥️  머신 ID: {get_machine_id()}")
    print()
    
    # 테스트 TXID (실제 서버가 없으면 실패)
    test_txid = "test_txid_12345"
    
    validator = LicenseValidator()
    is_valid = validator.validate(test_txid)
    
    print(f"✅ 라이선스 유효: {is_valid}")
    print(f"📊 상태: {validator.get_status()}")
    print()
    print("=" * 60)

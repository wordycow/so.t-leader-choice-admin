#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 모든 학습 데이터 완전 복구
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Git 히스토리에서 모든 학습 데이터를 복구합니다.
"""

import json
from emei_learning import get_emei

def restore_all_data():
    """모든 학습 데이터 완전 복구"""
    
    emei = get_emei()
    total_restored = 0
    
    print("🔄 모든 학습 데이터 완전 복구 시작...\n")
    
    # 1. free_learning_data.json (110개)
    print("=" * 60)
    print("📁 1. free_learning_data.json 복구")
    print("=" * 60)
    try:
        with open('/tmp/old_learning_data.json', 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        
        for item in data1:
            emei.save_knowledge(
                item['question'], 
                item['answer'], 
                f"restored_free_learning_{item.get('source', 'template')}"
            )
            total_restored += 1
        
        print(f"✅ {len(data1)}개 복구 완료")
    except Exception as e:
        print(f"⚠️ 오류: {e}")
    
    # 2. training_conversations.json (대화 데이터)
    print(f"\n{'=' * 60}")
    print("📁 2. training_conversations.json 복구")
    print("=" * 60)
    try:
        with open('/tmp/training_conversations.json', 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        count = 0
        for item in data2:
            question = item.get('user', '')
            answer = item.get('emei', '')
            
            if question and answer:
                emei.save_knowledge(
                    question, 
                    answer, 
                    'restored_training_conversations'
                )
                count += 1
                total_restored += 1
        
        print(f"✅ {count}개 복구 완료 (총 {len(data2)}개 중)")
    except Exception as e:
        print(f"⚠️ 오류: {e}")
    
    # 최종 통계
    print(f"\n{'=' * 60}")
    print("🎉 복구 완료!")
    print("=" * 60)
    
    stats = emei.get_stats()
    print(f"\n📊 현재 이메이 상태:")
    print(f"   학습된 지식: {stats['total_knowledge']}개")
    print(f"   대화 기록: {stats['total_conversations']}개")
    print(f"   학습률: {stats['learning_rate']}%")
    print(f"\n✨ 총 {total_restored}개 데이터 처리 완료!")

if __name__ == "__main__":
    restore_all_data()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 예전 학습 데이터 복구 스크립트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
110개의 예전 학습 데이터를 현재 DB로 복구합니다.
"""

import json
from emei_learning import get_emei

def restore_old_data():
    """예전 학습 데이터 복구"""
    
    # 이메이 시스템 초기화
    emei = get_emei()
    
    # 예전 학습 데이터 로드
    with open('/tmp/old_learning_data.json', 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    print(f"🔄 예전 학습 데이터 복구 시작...")
    print(f"   총 {len(old_data)}개 데이터")
    
    # 카테고리별 통계
    categories = {}
    
    # 데이터 복구
    restored_count = 0
    for i, item in enumerate(old_data, 1):
        question = item['question']
        answer = item['answer']
        category = item.get('category', 'general')
        source = f"restored_{item.get('source', 'template')}"
        
        # DB에 저장
        emei.save_knowledge(question, answer, source)
        
        # 통계
        categories[category] = categories.get(category, 0) + 1
        restored_count += 1
        
        if i % 20 == 0:
            print(f"   ✓ {i}/{len(old_data)} 복구 완료")
    
    print(f"\n✅ 복구 완료!")
    print(f"   총 {restored_count}개 데이터 복구됨")
    
    print(f"\n📊 카테고리별 통계:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}개")
    
    # 최종 통계
    stats = emei.get_stats()
    print(f"\n📊 현재 이메이 상태:")
    print(f"   학습된 지식: {stats['total_knowledge']}개 (28개 기본 + {restored_count}개 복구)")
    print(f"   대화 기록: {stats['total_conversations']}개")
    print(f"   학습률: {stats['learning_rate']}%")

if __name__ == "__main__":
    restore_old_data()

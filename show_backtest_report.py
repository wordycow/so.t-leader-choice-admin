#!/usr/bin/env python3
import json

with open('backtest_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("\n" + "="*80)
print("📊 패턴 인식 백테스팅 최종 리포트")
print("="*80)

print(f"\n⏰ 테스트 시간: {data['timestamp']}")
print(f"🎯 테스트 코인: {len(data['test_coins'])}개")
print(f"   {', '.join([c.replace('KRW-', '') for c in data['test_coins']])}")

print("\n" + "="*80)
print("🏆 전략별 성과 순위")
print("="*80)

# 전략별 점수 계산 및 정렬
strategies = []
for strat_id, summary in data['strategy_summary'].items():
    score = summary['win_rate'] * summary['avg_profit']
    strategies.append({
        'name': summary['name'],
        'signals': summary['total_signals'],
        'win_rate': summary['win_rate'],
        'avg_profit': summary['avg_profit'],
        'score': score
    })

strategies.sort(key=lambda x: x['score'], reverse=True)

for i, strat in enumerate(strategies, 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
    print(f"\n{medal} {strat['name']}")
    print(f"   신호: {strat['signals']}회")
    print(f"   승률: {strat['win_rate']:.1f}%")
    print(f"   평균 수익: {strat['avg_profit']:.2f}%")
    print(f"   종합 점수: {strat['score']:.1f}")

print("\n" + "="*80)
print("💡 추천 사항")
print("="*80)

best = strategies[0]
print(f"\n✅ 최고 성능: {best['name']}")
print(f"   - 가장 높은 종합 점수 ({best['score']:.1f})")
print(f"   - 승률 {best['win_rate']:.1f}%, 평균 수익 {best['avg_profit']:.2f}%")

print(f"\n✅ 실전 추천 조합:")
print(f"   1순위: {strategies[0]['name']} (가장 안정적)")
print(f"   2순위: {strategies[1]['name']} (보조 전략)")
print(f"   3순위: {strategies[2]['name']} (다각화)")

print("\n" + "="*80)
print("📈 코인별 최고 성과")
print("="*80)

for coin_result in data['coin_results']:
    ticker = coin_result['ticker'].replace('KRW-', '')
    best_strat = None
    best_win_rate = 0
    
    for strat_id, strat_data in coin_result['strategies'].items():
        if strat_data['total_signals'] > 0 and strat_data.get('win_rate', 0) > best_win_rate:
            best_win_rate = strat_data['win_rate']
            best_strat = strat_data['name']
    
    if best_strat:
        print(f"\n💎 {ticker}: {best_strat} (승률 {best_win_rate:.1f}%)")

print("\n" + "="*80)

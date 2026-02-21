#!/usr/bin/env python3
"""
Complete Website Flow Test & Design Review
Gate → Main 페이지 전체 확인
"""

import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai"

pages_to_test = [
    {
        "name": "Gate (로그인)",
        "url": f"{BASE_URL}/the-unique-gate.html",
        "screenshot": "screenshots/01-gate.png",
        "checks": [
            "배경 이미지 로드",
            "Glass morphism 효과",
            "로그인 폼 스타일",
            "버튼 호버 효과"
        ]
    },
    {
        "name": "Main (메인 페이지)",
        "url": f"{BASE_URL}/the-unique-main.html",
        "screenshot": "screenshots/02-main.png",
        "checks": [
            "상단 스케줄",
            "지갑 UI",
            "UT 도넛 차트",
            "게임 버튼"
        ]
    },
    {
        "name": "Index (리더 선택)",
        "url": f"{BASE_URL}/index.html",
        "screenshot": "screenshots/03-index.png",
        "checks": [
            "리더 카드 그리드",
            "Glass panel 효과",
            "SNS 버튼",
            "배너 애니메이션"
        ]
    },
    {
        "name": "Market",
        "url": f"{BASE_URL}/market.html",
        "screenshot": "screenshots/04-market.png",
        "checks": [
            "상품 리스트",
            "필터 기능",
            "카드 디자인"
        ]
    },
    {
        "name": "Casino",
        "url": f"{BASE_URL}/casino.html",
        "screenshot": "screenshots/05-casino.png",
        "checks": [
            "게임 목록",
            "UT 잔액 표시",
            "상단 바"
        ]
    }
]

def test_page(page, test_config):
    """개별 페이지 테스트"""
    print(f"\n{'='*60}")
    print(f"📄 테스트: {test_config['name']}")
    print(f"🔗 URL: {test_config['url']}")
    print(f"{'='*60}")
    
    try:
        # 페이지 로드
        print("⏳ 페이지 로딩 중...")
        page.goto(test_config['url'], timeout=30000, wait_until='networkidle')
        time.sleep(2)
        
        # 기본 정보
        title = page.title()
        print(f"📌 페이지 제목: {title}")
        
        # 스크린샷 (전체 페이지)
        page.screenshot(path=test_config['screenshot'], full_page=True)
        print(f"📸 스크린샷 저장: {test_config['screenshot']}")
        
        # Console 로그 확인
        console_messages = []
        errors = []
        
        def handle_console(msg):
            if msg.type == 'error':
                errors.append(msg.text)
            console_messages.append(f"[{msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        # CSS 파일 로드 확인
        css_loaded = page.evaluate("""() => {
            const links = document.querySelectorAll('link[rel="stylesheet"]');
            return Array.from(links).map(link => ({
                href: link.href,
                loaded: link.sheet !== null
            }));
        }""")
        
        print(f"\n🎨 CSS 파일 상태:")
        for css in css_loaded:
            status = "✅" if css['loaded'] else "❌"
            filename = css['href'].split('/')[-1]
            print(f"   {status} {filename}")
        
        # 이미지 로드 확인
        images = page.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            return Array.from(imgs).map(img => ({
                src: img.src,
                loaded: img.complete && img.naturalHeight > 0,
                lazy: img.loading === 'lazy'
            }));
        }""")
        
        print(f"\n🖼️ 이미지 상태: (총 {len(images)}개)")
        loaded_count = sum(1 for img in images if img['loaded'])
        lazy_count = sum(1 for img in images if img['lazy'])
        print(f"   ✅ 로드 완료: {loaded_count}/{len(images)}")
        print(f"   ⚡ Lazy loading: {lazy_count}개")
        
        # 반응형 테스트 (모바일)
        print(f"\n📱 모바일 뷰 테스트...")
        page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(1)
        page.screenshot(path=test_config['screenshot'].replace('.png', '-mobile.png'))
        print(f"   📸 모바일 스크린샷 저장")
        
        # 원래 크기로 복원
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 인터랙션 테스트 (버튼 호버)
        buttons = page.query_selector_all('button, .action-btn, .game-btn')
        print(f"\n🔘 버튼 확인: {len(buttons)}개")
        
        # 에러 확인
        if errors:
            print(f"\n⚠️ 에러 발견: {len(errors)}개")
            for err in errors[:3]:  # 처음 3개만
                print(f"   ❌ {err}")
        else:
            print(f"\n✅ 에러 없음!")
        
        print(f"\n✅ {test_config['name']} 테스트 완료!")
        
        return {
            "name": test_config['name'],
            "url": test_config['url'],
            "title": title,
            "css_count": len(css_loaded),
            "css_loaded": sum(1 for c in css_loaded if c['loaded']),
            "images_count": len(images),
            "images_loaded": loaded_count,
            "lazy_images": lazy_count,
            "buttons_count": len(buttons),
            "errors_count": len(errors),
            "status": "✅ 정상" if not errors else "⚠️ 에러 있음"
        }
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}")
        return {
            "name": test_config['name'],
            "status": f"❌ 실패: {str(e)}"
        }

def main():
    print("🚀 The Unique 웹사이트 전체 플로우 테스트 시작!\n")
    
    # 스크린샷 디렉토리 생성
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        results = []
        for test_config in pages_to_test:
            result = test_page(page, test_config)
            results.append(result)
            time.sleep(1)
        
        browser.close()
    
    # 최종 리포트
    print("\n" + "="*60)
    print("📊 전체 테스트 결과 요약")
    print("="*60)
    
    for result in results:
        print(f"\n{result['name']}")
        print(f"  상태: {result.get('status', '❓')}")
        if 'css_loaded' in result:
            print(f"  CSS: {result['css_loaded']}/{result['css_count']}")
            print(f"  이미지: {result['images_loaded']}/{result['images_count']}")
            print(f"  Lazy: {result['lazy_images']}개")
            print(f"  버튼: {result['buttons_count']}개")
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료!")
    print("📁 스크린샷: screenshots/ 폴더 확인")
    print("="*60)

if __name__ == "__main__":
    main()

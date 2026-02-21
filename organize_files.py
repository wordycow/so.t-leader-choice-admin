import os
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 기준 날짜 (10일 전)
cutoff_date = datetime.now() - timedelta(days=10)

# 폴더 생성
folders = {
    'original_unique': {
        'bat': 'original_unique/batch_files',
        'md': 'original_unique/docs',
        'html': 'original_unique/html_files',
        'py': 'original_unique/python_files',
        'js': 'original_unique/javascript_files',
        'json': 'original_unique/config_files',
        'other': 'original_unique/other_files'
    },
    'new_files': {
        'bat': 'new_files/batch_files',
        'md': 'new_files/docs',
        'html': 'new_files/html_files',
        'py': 'new_files/python_files',
        'js': 'new_files/javascript_files',
        'json': 'new_files/config_files',
        'other': 'new_files/other_files'
    }
}

# 폴더 생성
for category in folders.values():
    for folder in category.values():
        os.makedirs(folder, exist_ok=True)

# Git에서 파일 목록과 날짜 가져오기
result = subprocess.run(
    ['git', 'ls-files'],
    capture_output=True,
    text=True,
    cwd='/home/user/webapp'
)

files = result.stdout.strip().split('\n')

stats = {
    'original': 0,
    'new': 0,
    'by_ext': {}
}

for file in files:
    if not file or not os.path.exists(file):
        continue
    
    # Git 날짜 확인
    date_result = subprocess.run(
        ['git', 'log', '-1', '--format=%ad', '--date=short', '--', file],
        capture_output=True,
        text=True,
        cwd='/home/user/webapp'
    )
    
    date_str = date_result.stdout.strip()
    if not date_str:
        continue
    
    file_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 파일 확장자 확인
    ext = Path(file).suffix.lower().lstrip('.')
    if ext not in ['bat', 'md', 'html', 'py', 'js', 'json']:
        ext = 'other'
    
    # 통계
    if ext not in stats['by_ext']:
        stats['by_ext'][ext] = {'original': 0, 'new': 0}
    
    # 분류
    if file_date < cutoff_date:
        category = 'original_unique'
        stats['original'] += 1
        stats['by_ext'][ext]['original'] += 1
    else:
        category = 'new_files'
        stats['new'] += 1
        stats['by_ext'][ext]['new'] += 1
    
    # 대상 폴더
    target_folder = folders[category][ext]
    target_path = os.path.join(target_folder, os.path.basename(file))
    
    # 중복 처리
    if os.path.exists(target_path):
        base, extension = os.path.splitext(os.path.basename(file))
        counter = 1
        while os.path.exists(target_path):
            target_path = os.path.join(target_folder, f"{base}_{counter}{extension}")
            counter += 1
    
    # 복사
    try:
        shutil.copy2(file, target_path)
    except Exception as e:
        print(f"Error copying {file}: {e}")

# 통계 출력
print("\n=== 파일 분류 완료 ===")
print(f"\n총 파일 수:")
print(f"  - Original (10일 이전): {stats['original']}개")
print(f"  - New (10일 이내): {stats['new']}개")
print(f"\n파일 유형별 분류:")
for ext, counts in sorted(stats['by_ext'].items()):
    print(f"  {ext.upper()}:")
    print(f"    - Original: {counts['original']}개")
    print(f"    - New: {counts['new']}개")

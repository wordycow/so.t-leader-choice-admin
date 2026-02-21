import os
import subprocess
from pathlib import Path

# original_unique 폴더에서 파일 목록 가져오기
original_files = []
for root, dirs, files in os.walk('original_unique'):
    for file in files:
        original_files.append(os.path.basename(file))

print(f"Original 파일 수: {len(original_files)}개")

# Git에서 추적 중인 파일 중 original에 해당하는 파일 찾기
result = subprocess.run(
    ['git', 'ls-files'],
    capture_output=True,
    text=True,
    cwd='/home/user/webapp'
)

git_files = result.stdout.strip().split('\n')

# 삭제할 파일 목록
files_to_delete = []
for git_file in git_files:
    # organized 폴더 내부 파일은 제외
    if git_file.startswith('original_unique/') or git_file.startswith('new_files/'):
        continue
    
    basename = os.path.basename(git_file)
    if basename in original_files:
        files_to_delete.append(git_file)

print(f"\n삭제할 파일 수: {len(files_to_delete)}개")
print("\n삭제할 파일 목록 (처음 20개):")
for i, file in enumerate(files_to_delete[:20]):
    print(f"  {i+1}. {file}")

if len(files_to_delete) > 20:
    print(f"  ... 외 {len(files_to_delete) - 20}개")

# 파일 삭제 실행
if files_to_delete:
    print("\n파일 삭제 중...")
    for file in files_to_delete:
        try:
            subprocess.run(['git', 'rm', file], cwd='/home/user/webapp', check=True)
            print(f"  삭제: {file}")
        except subprocess.CalledProcessError as e:
            print(f"  오류: {file} - {e}")
    
    print(f"\n총 {len(files_to_delete)}개 파일 삭제 완료")
else:
    print("\n삭제할 파일이 없습니다.")

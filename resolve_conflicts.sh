#!/bin/bash

while true; do
    # 충돌 파일 확인
    conflicts=$(git status --porcelain | grep "^DU\|^UD\|^AA\|^UU" | awk '{print $2}')
    
    if [ -z "$conflicts" ]; then
        # 충돌이 없으면 cherry-pick 계속
        git cherry-pick --continue
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo "체리픽 완료!"
            break
        elif [ $exit_code -eq 128 ]; then
            echo "체리픽 프로세스 완료"
            break
        fi
    else
        # 충돌 파일 처리
        for file in $conflicts; do
            status=$(git status --porcelain "$file" | cut -c1-2)
            
            if [[ "$status" == "DU" ]]; then
                # deleted by us - 원격 버전 사용
                echo "Accepting theirs for: $file"
                git add "$file"
            elif [[ "$status" == "UD" ]]; then
                # deleted by them - 삭제 수용
                echo "Accepting deletion for: $file"
                git rm "$file"
            elif [[ "$status" == "UU" ]] || [[ "$status" == "AA" ]]; then
                # both modified - 원격 버전 우선
                echo "Using theirs for: $file"
                git checkout --theirs "$file"
                git add "$file"
            fi
        done
        
        # 변경사항 커밋
        git cherry-pick --continue
        
        if [ $? -ne 0 ]; then
            echo "체리픽 중단 또는 완료"
            break
        fi
    fi
done

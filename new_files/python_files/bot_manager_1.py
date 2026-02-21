# -*- coding: utf-8 -*-
"""
Lee May Training Center - Bot Manager
모든 봇을 제어하는 중앙 관리 시스템
"""

import psutil
import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, Optional

class BotManager:
    """봇 프로세스 관리자"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.pids_file = self.base_dir / "data" / "pids.json"
        self.pids_file.parent.mkdir(parents=True, exist_ok=True)
        self.pids = self.load_pids()
        
        print("✅ Bot Manager 초기화 완료")
    
    def is_process_running(self, pid: int) -> bool:
        """PID로 프로세스 실행 여부 확인"""
        try:
            return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
        except:
            return False
    
    def find_process_by_name(self, name: str) -> Optional[psutil.Process]:
        """프로세스 이름으로 찾기"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if name.lower() in cmdline.lower():
                    return proc
            except:
                continue
        return None
    
    def get_leemay_api_status(self) -> Dict:
        """Lee May API 서버 상태"""
        proc = self.find_process_by_name('api_server.py')
        
        if proc:
            try:
                return {
                    "running": True,
                    "pid": proc.pid,
                    "cpu": round(proc.cpu_percent(), 1),
                    "memory": round(proc.memory_percent(), 1),
                    "uptime": int(time.time() - proc.create_time())
                }
            except:
                pass
        
        return {"running": False}
    
    def get_ollama_tunnel_status(self) -> Dict:
        """Ollama Cloudflare Tunnel 상태"""
        proc = self.find_process_by_name('cloudflared')
        
        if proc:
            try:
                cmdline = ' '.join(proc.cmdline())
                
                # ollama-stable 터널인지 확인
                if 'ollama' in cmdline.lower():
                    return {
                        "running": True,
                        "pid": proc.pid,
                        "cpu": round(proc.cpu_percent(), 1),
                        "memory": round(proc.memory_percent(), 1),
                        "tunnel_name": "ollama-stable"
                    }
            except:
                pass
        
        return {"running": False}
    
    def get_youtube_learner_status(self) -> Dict:
        """YouTube Learner 상태"""
        proc = self.find_process_by_name('youtube_smart_learner.py')
        
        if proc:
            try:
                return {
                    "running": True,
                    "pid": proc.pid,
                    "cpu": round(proc.cpu_percent(), 1),
                    "memory": round(proc.memory_percent(), 1)
                }
            except:
                pass
        
        return {"running": False}
    
    def get_all_status(self) -> Dict:
        """모든 봇 상태 조회"""
        return {
            "leemay_api": self.get_leemay_api_status(),
            "ollama_tunnel": self.get_ollama_tunnel_status(),
            "youtube_learner": self.get_youtube_learner_status()
        }
    
    def start_bot(self, bot_name: str) -> Dict:
        """봇 시작"""
        if bot_name == "leemay_api":
            return self._start_leemay_api()
        elif bot_name == "ollama_tunnel":
            return self._start_ollama_tunnel()
        elif bot_name == "youtube_learner":
            return self._start_youtube_learner()
        else:
            return {"success": False, "error": f"알 수 없는 봇: {bot_name}"}
    
    def _start_leemay_api(self) -> Dict:
        """Lee May API 서버 시작"""
        if self.get_leemay_api_status()["running"]:
            return {"success": False, "error": "이미 실행 중"}
        
        try:
            script_path = self.base_dir / "api_server.py"
            process = subprocess.Popen(
                ["python", str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)  # 시작 대기
            
            if self.is_process_running(process.pid):
                return {
                    "success": True,
                    "pid": process.pid,
                    "message": "Lee May API 서버 시작됨"
                }
            else:
                return {"success": False, "error": "시작 실패"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _start_ollama_tunnel(self) -> Dict:
        """Ollama Tunnel 시작"""
        if self.get_ollama_tunnel_status()["running"]:
            return {"success": False, "error": "이미 실행 중"}
        
        try:
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "run", "ollama-stable"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.is_process_running(process.pid):
                return {
                    "success": True,
                    "pid": process.pid,
                    "message": "Ollama Tunnel 시작됨"
                }
            else:
                return {"success": False, "error": "시작 실패"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _start_youtube_learner(self) -> Dict:
        """YouTube Learner 시작"""
        return {"success": False, "error": "수동 실행 필요"}
    
    def stop_bot(self, bot_name: str) -> Dict:
        """봇 중지"""
        status = self.get_all_status().get(bot_name, {})
        
        if not status.get("running"):
            return {"success": False, "error": "실행 중이 아님"}
        
        try:
            pid = status["pid"]
            process = psutil.Process(pid)
            process.terminate()
            
            time.sleep(1)
            
            if psutil.pid_exists(pid):
                process.kill()
            
            return {"success": True, "message": f"{bot_name} 중지됨"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_bot(self, bot_name: str) -> Dict:
        """봇 재시작"""
        stop_result = self.stop_bot(bot_name)
        if not stop_result.get("success"):
            return stop_result
        
        time.sleep(2)
        return self.start_bot(bot_name)
    
    def load_pids(self) -> Dict:
        """PID 파일 로드"""
        try:
            if self.pids_file.exists():
                with open(self.pids_file) as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_pids(self):
        """PID 파일 저장"""
        with open(self.pids_file, "w") as f:
            json.dump(self.pids, f, indent=2)

# 테스트
if __name__ == "__main__":
    manager = BotManager()
    print("\n📊 현재 봇 상태:")
    print(json.dumps(manager.get_all_status(), indent=2, ensure_ascii=False))

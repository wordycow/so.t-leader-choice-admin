Set objShell = CreateObject("WScript.Shell")

' ============================================================
' Lee May Training Center - 통합 시작 스크립트
' ============================================================

' 1. API 서버 시작 (백그라운드)
Dim strAPICommand
strAPICommand = "cmd /c cd C:\leemay_project && python api_server.py"
objShell.Run strAPICommand, 0, False

' 2. Cloudflare 터널 시작 (백그라운드)
Dim strTunnelCommand
strTunnelCommand = "cmd /c cloudflared tunnel run --url http://localhost:5001 ollama-stable"
objShell.Run strTunnelCommand, 0, False

' 3. 완료 메시지
WScript.Sleep 5000
objShell.Popup "🚀 Lee May Training Center 시작 완료!" & vbCrLf & vbCrLf & _
              "📍 로컬: http://localhost:5001" & vbCrLf & _
              "🌐 외부: https://leemay.thetheunique.com" & vbCrLf & vbCrLf & _
              "🎭 4대 핵심 모듈 가동 중:" & vbCrLf & _
              "  ✅ Emotion Engine" & vbCrLf & _
              "  ✅ Knowledge RAG" & vbCrLf & _
              "  ✅ Live Telemetry" & vbCrLf & _
              "  ✅ Central Command", 10, "Lee May Training Center", 64

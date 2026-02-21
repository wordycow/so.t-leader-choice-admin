# update_playlist.ps1
# 사용: 프로젝트 루트에서 PowerShell로 실행
# 결과: games/roulette.playlist.js 자동 생성 (기존 + 신규 합쳐서 중복 제거 후 150개)

$ErrorActionPreference = "Stop"

# ✅ 여기에 플레이리스트 URL만 넣어줘 (여러 개 가능)
$Playlists = @(
  # "https://www.youtube.com/playlist?list=XXXXXXXXXXXX",
  # "https://www.youtube.com/playlist?list=YYYYYYYYYYYY"
)

# --- 경로 ---
$Root = Get-Location
$GamesDir = Join-Path $Root "games"
$OutJs = Join-Path $GamesDir "roulette.playlist.js"

if (!(Test-Path $GamesDir)) {
  throw "games 폴더가 없어요. 지금 위치가 프로젝트 루트가 맞는지 확인해줘요: $Root"
}

# --- yt-dlp 체크 ---
$ytdlp = (Get-Command yt-dlp -ErrorAction SilentlyContinue)
if (-not $ytdlp) {
  throw "yt-dlp가 설치 안 되어 있어요. 먼저: winget install yt-dlp.yt-dlp"
}

# --- 기존 JS에서 ID 뽑기 ---
$IdRegex = [regex]'\b[A-Za-z0-9_-]{11}\b'
$baseIds = @()

if (Test-Path $OutJs) {
  $txt = Get-Content $OutJs -Raw
  $baseIds = $IdRegex.Matches($txt) | ForEach-Object { $_.Value }
}

# --- 새 플레이리스트에서 ID 뽑기 ---
$newIds = @()

if ($Playlists.Count -eq 0) {
  Write-Host "⚠️ Playlists가 비어있어요. update_playlist.ps1 안에 URL을 넣어주세요." -ForegroundColor Yellow
  Write-Host "그래도 기존 roulette.playlist.js에서 ID만 정리해서 150개로 저장할게요." -ForegroundColor Yellow
} else {
  foreach ($url in $Playlists) {
    if ([string]::IsNullOrWhiteSpace($url)) { continue }
    Write-Host "▶ Fetching: $url"
    $out = yt-dlp --flat-playlist --print id $url 2>$null
    if ($out) {
      $lines = $out -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^[A-Za-z0-9_-]{11}$' }
      $newIds += $lines
    }
  }
}

# --- 중복 제거(순서 유지) ---
function Unique-KeepOrder($arr) {
  $seen = New-Object 'System.Collections.Generic.HashSet[string]'
  $out = New-Object 'System.Collections.Generic.List[string]'
  foreach ($x in $arr) {
    if ($seen.Add($x)) { $out.Add($x) | Out-Null }
  }
  return ,$out
}

$merged = Unique-KeepOrder ($baseIds + $newIds)
$before = $merged.Count

# --- 150개로 컷 ---
$maxN = 150
if ($merged.Count -gt $maxN) {
  $merged = $merged[0..($maxN-1)]
}

# --- JS 파일로 저장 ---
$header = @"
/* THE UNIQUE - ROYAL ROULETTE Playlist
   - roulette.html과 같은 폴더(/games/)에 두세요.
   - update_playlist.ps1로 자동 생성됨
*/
window.UNIQUE_YT_PLAYLIST = [
"@

$body = ($merged | ForEach-Object { "  `"$_`"," }) -join "`n"
$footer = @"
];
"@

$final = $header + "`n" + $body + "`n" + $footer
Set-Content -Path $OutJs -Value $final -Encoding UTF8

Write-Host ""
Write-Host "✅ 완료!" -ForegroundColor Green
Write-Host "base(기존): $($baseIds.Count)개"
Write-Host "new(신규):  $($newIds.Count)개"
Write-Host "merged unique: $before 개 → saved: $($merged.Count)개"
Write-Host "written: $OutJs"

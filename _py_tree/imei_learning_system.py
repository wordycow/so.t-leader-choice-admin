#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMEI 무료 학습 시스템
- YouTube 영상 자막 추출 및 학습
- 웹페이지 크롤링 및 학습
- 대화 기록 기반 학습
- SQLite 기반 영구 메모리
"""

import sqlite3
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional
import re
import os

class IMEILearningSystem:
    def __init__(self, db_path='imei_knowledge.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 지식 베이스 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,  -- youtube, web, conversation, manual
                source_url TEXT,
                content_hash TEXT UNIQUE,
                title TEXT,
                content TEXT NOT NULL,
                summary TEXT,
                tags TEXT,  -- JSON array
                importance INTEGER DEFAULT 1,  -- 1-5
                created_at TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # 유튜브 영상 학습 기록
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_url TEXT UNIQUE,
                title TEXT,
                transcript TEXT,
                summary TEXT,
                key_points TEXT,  -- JSON array
                learned_at TEXT,
                status TEXT DEFAULT 'pending'  -- pending, processed, failed
            )
        ''')
        
        # 대화 학습 기록
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                context TEXT,
                response TEXT,
                feedback TEXT,  -- positive, negative, neutral
                learned_at TEXT
            )
        ''')
        
        # 농담 및 유머 데이터베이스
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jokes_humor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,  -- joke, pun, meme, sarcasm
                content TEXT,
                context TEXT,
                source TEXT,
                rating INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # 트레이딩 전략 학습
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT,
                description TEXT,
                indicators TEXT,  -- JSON
                conditions TEXT,  -- JSON
                success_rate REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                profitable_trades INTEGER DEFAULT 0,
                learned_from TEXT,  -- youtube, backtest, live
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # 시장 패턴 학습
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                description TEXT,
                indicators TEXT,  -- JSON
                historical_accuracy REAL,
                occurrence_count INTEGER DEFAULT 0,
                last_seen TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def learn_from_youtube(self, video_url: str) -> Dict:
        """
        YouTube 영상에서 학습
        1. 영상 ID 추출
        2. 자막 다운로드 (youtube-transcript-api 사용)
        3. 내용 분석 및 요약
        4. 데이터베이스 저장
        """
        try:
            # YouTube 영상 ID 추출
            video_id = self._extract_youtube_id(video_url)
            if not video_id:
                return {"success": False, "error": "Invalid YouTube URL"}
            
            # 이미 학습했는지 확인
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, status FROM youtube_videos WHERE video_url = ?', (video_url,))
            existing = cursor.fetchone()
            
            if existing and existing[1] == 'processed':
                conn.close()
                return {"success": True, "message": "Already learned", "cached": True}
            
            # 자막 다운로드 (실제 구현 시 youtube-transcript-api 사용)
            # pip install youtube-transcript-api
            transcript = self._download_youtube_transcript(video_id)
            
            if not transcript:
                cursor.execute('''
                    INSERT OR REPLACE INTO youtube_videos (video_url, status, learned_at)
                    VALUES (?, 'failed', ?)
                ''', (video_url, datetime.now().isoformat()))
                conn.commit()
                conn.close()
                return {"success": False, "error": "Transcript not available"}
            
            # 내용 분석
            title = self._get_video_title(video_id)
            summary = self._summarize_text(transcript)
            key_points = self._extract_key_points(transcript)
            
            # 지식 베이스에 저장
            content_hash = hashlib.md5(transcript.encode()).hexdigest()
            tags = self._extract_tags(transcript)
            
            cursor.execute('''
                INSERT INTO knowledge_base 
                (source_type, source_url, content_hash, title, content, summary, tags, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('youtube', video_url, content_hash, title, transcript, summary, 
                  json.dumps(tags), datetime.now().isoformat(), datetime.now().isoformat()))
            
            # YouTube 기록 저장
            cursor.execute('''
                INSERT OR REPLACE INTO youtube_videos 
                (video_url, title, transcript, summary, key_points, status, learned_at)
                VALUES (?, ?, ?, ?, ?, 'processed', ?)
            ''', (video_url, title, transcript, summary, json.dumps(key_points), 
                  datetime.now().isoformat()))
            
            # 트레이딩 관련 내용이면 전략 추출
            if self._is_trading_related(transcript):
                strategies = self._extract_trading_strategies(transcript)
                for strategy in strategies:
                    cursor.execute('''
                        INSERT INTO trading_strategies 
                        (strategy_name, description, indicators, conditions, learned_from, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (strategy['name'], strategy['description'], 
                          json.dumps(strategy['indicators']), 
                          json.dumps(strategy['conditions']),
                          video_url, datetime.now().isoformat(), datetime.now().isoformat()))
            
            # 유머/농담 추출
            jokes = self._extract_humor(transcript)
            for joke in jokes:
                cursor.execute('''
                    INSERT INTO jokes_humor (category, content, source, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (joke['category'], joke['content'], video_url, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "title": title,
                "summary": summary,
                "key_points": key_points,
                "strategies_learned": len(strategies) if 'strategies' in locals() else 0,
                "jokes_learned": len(jokes)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def learn_from_conversation(self, user_message: str, bot_response: str, 
                                feedback: str = "neutral", context: str = ""):
        """대화에서 학습"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_patterns 
            (user_message, context, response, feedback, learned_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_message, context, bot_response, feedback, datetime.now().isoformat()))
        
        # 긍정적 피드백이면 지식 베이스에도 저장
        if feedback == "positive":
            content = f"Q: {user_message}\nA: {bot_response}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            cursor.execute('''
                INSERT OR IGNORE INTO knowledge_base 
                (source_type, content_hash, content, tags, importance, created_at, last_accessed)
                VALUES (?, ?, ?, ?, 3, ?, ?)
            ''', ('conversation', content_hash, content, json.dumps(['conversation', 'qa']),
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """지식 베이스 검색"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 간단한 키워드 검색 (실제로는 더 복잡한 검색 알고리즘 필요)
        keywords = query.lower().split()
        results = []
        
        cursor.execute('''
            SELECT id, source_type, title, content, summary, tags, importance, access_count
            FROM knowledge_base
            ORDER BY importance DESC, access_count DESC
            LIMIT ?
        ''', (limit * 3,))
        
        all_results = cursor.fetchall()
        
        # 키워드 매칭
        for row in all_results:
            content_lower = (row[3] + " " + (row[4] or "")).lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            
            if score > 0:
                results.append({
                    "id": row[0],
                    "source_type": row[1],
                    "title": row[2],
                    "content": row[3][:500],  # 처음 500자만
                    "summary": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "importance": row[6],
                    "score": score
                })
                
                # 접근 카운트 증가
                cursor.execute('UPDATE knowledge_base SET access_count = access_count + 1, last_accessed = ? WHERE id = ?',
                             (datetime.now().isoformat(), row[0]))
        
        conn.commit()
        conn.close()
        
        # 점수 순 정렬
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_trading_strategy(self, strategy_name: Optional[str] = None) -> List[Dict]:
        """트레이딩 전략 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if strategy_name:
            cursor.execute('''
                SELECT strategy_name, description, indicators, conditions, 
                       success_rate, total_trades, profitable_trades
                FROM trading_strategies
                WHERE strategy_name LIKE ?
                ORDER BY success_rate DESC
            ''', (f'%{strategy_name}%',))
        else:
            cursor.execute('''
                SELECT strategy_name, description, indicators, conditions, 
                       success_rate, total_trades, profitable_trades
                FROM trading_strategies
                ORDER BY success_rate DESC
                LIMIT 10
            ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "strategy_name": row[0],
                "description": row[1],
                "indicators": json.loads(row[2]) if row[2] else [],
                "conditions": json.loads(row[3]) if row[3] else [],
                "success_rate": row[4],
                "total_trades": row[5],
                "profitable_trades": row[6]
            })
        
        conn.close()
        return results
    
    def update_strategy_performance(self, strategy_name: str, is_profitable: bool):
        """전략 성과 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE trading_strategies
            SET total_trades = total_trades + 1,
                profitable_trades = profitable_trades + ?,
                success_rate = CAST(profitable_trades AS REAL) / total_trades,
                updated_at = ?
            WHERE strategy_name = ?
        ''', (1 if is_profitable else 0, datetime.now().isoformat(), strategy_name))
        
        conn.commit()
        conn.close()
    
    def get_random_joke(self, category: Optional[str] = None) -> Optional[str]:
        """랜덤 농담 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT content FROM jokes_humor 
                WHERE category = ?
                ORDER BY RANDOM()
                LIMIT 1
            ''', (category,))
        else:
            cursor.execute('''
                SELECT content FROM jokes_humor 
                ORDER BY RANDOM()
                LIMIT 1
            ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_statistics(self) -> Dict:
        """학습 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_base')
        stats['total_knowledge'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM youtube_videos WHERE status = "processed"')
        stats['youtube_videos_learned'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conversation_patterns')
        stats['conversations_learned'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jokes_humor')
        stats['jokes_learned'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM trading_strategies')
        stats['strategies_learned'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT AVG(success_rate) FROM trading_strategies 
            WHERE total_trades > 0
        ''')
        avg_rate = cursor.fetchone()[0]
        stats['average_strategy_success_rate'] = round(avg_rate * 100, 2) if avg_rate else 0
        
        conn.close()
        return stats
    
    # 헬퍼 메서드들
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 영상 ID 추출"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
            r'youtube\.com\/embed\/([^&\n?]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _download_youtube_transcript(self, video_id: str) -> Optional[str]:
        """YouTube 자막 다운로드 (실제 구현 필요)"""
        # 실제 구현:
        # from youtube_transcript_api import YouTubeTranscriptApi
        # transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        # return ' '.join([entry['text'] for entry in transcript])
        
        # 임시 구현 (테스트용)
        return f"[임시] {video_id} 영상의 자막 내용..."
    
    def _get_video_title(self, video_id: str) -> str:
        """YouTube 영상 제목 가져오기"""
        # 실제 구현: YouTube Data API 사용
        return f"[임시] 영상 제목 {video_id}"
    
    def _summarize_text(self, text: str) -> str:
        """텍스트 요약 (간단한 버전)"""
        sentences = text.split('.')[:3]
        return '.'.join(sentences) + '...'
    
    def _extract_key_points(self, text: str) -> List[str]:
        """핵심 포인트 추출"""
        # 간단한 구현 (실제로는 NLP 기술 필요)
        sentences = text.split('.')[:5]
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _extract_tags(self, text: str) -> List[str]:
        """태그 추출"""
        # 간단한 키워드 추출
        keywords = ['트레이딩', '비트코인', '전략', '투자', '코인', '차트', 'RSI', 'MACD']
        found_tags = [kw for kw in keywords if kw.lower() in text.lower()]
        return found_tags if found_tags else ['general']
    
    def _is_trading_related(self, text: str) -> bool:
        """트레이딩 관련 내용인지 확인"""
        keywords = ['트레이딩', '매매', '전략', '투자', '코인', '비트코인', '차트', '지표']
        return any(kw in text.lower() for kw in keywords)
    
    def _extract_trading_strategies(self, text: str) -> List[Dict]:
        """트레이딩 전략 추출"""
        # 간단한 구현 (실제로는 더 정교한 분석 필요)
        strategies = []
        
        if 'RSI' in text.upper():
            strategies.append({
                "name": "RSI 기반 전략",
                "description": "RSI 지표를 활용한 과매수/과매도 전략",
                "indicators": ["RSI"],
                "conditions": ["RSI < 30: BUY", "RSI > 70: SELL"]
            })
        
        return strategies
    
    def _extract_humor(self, text: str) -> List[Dict]:
        """유머/농담 추출"""
        # 간단한 구현
        jokes = []
        
        # 이모티콘이 있는 문장 찾기
        if any(emoji in text for emoji in ['😂', '🤣', 'ㅋㅋ', 'ㅎㅎ']):
            sentences = text.split('.')
            for sentence in sentences:
                if any(emoji in sentence for emoji in ['😂', '🤣', 'ㅋㅋ', 'ㅎㅎ']):
                    jokes.append({
                        "category": "humor",
                        "content": sentence.strip()
                    })
        
        return jokes

if __name__ == "__main__":
    # 테스트
    learning = IMEILearningSystem()
    
    # 통계 출력
    stats = learning.get_statistics()
    print("📊 IMEI 학습 통계:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")

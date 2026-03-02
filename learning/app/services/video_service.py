import os
import re
import json
import subprocess
import yt_dlp
from typing import Optional, Dict, List
from pathlib import Path
import httpx
from app.config import settings


class VideoDownloader:
    def __init__(self):
        self.storage_path = Path(settings.VIDEO_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def download_douyin_video(self, url: str) -> Optional[Dict]:
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(self.storage_path / 'douyin_%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                video_id = info.get('id', '')
                title = info.get('title', '')
                author = info.get('uploader', '')
                duration = info.get('duration', 0)
                description = info.get('description', '')
                
                audio_path = str(self.storage_path / f'douyin_{video_id}.mp3')
                
                return {
                    'video_id': video_id,
                    'video_url': url,
                    'title': title,
                    'author': author,
                    'duration': duration,
                    'description': description,
                    'audio_path': audio_path if os.path.exists(audio_path) else None
                }
        except Exception as e:
            print(f"Error downloading Douyin video: {e}")
            return None
    
    def download_bilibili_video(self, url: str) -> Optional[Dict]:
        try:
            video_id = self._extract_bilibili_id(url)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.storage_path / 'bilibili_%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                title = info.get('title', '')
                author = info.get('uploader', '')
                duration = info.get('duration', 0)
                description = info.get('description', '')
                subtitles = info.get('subtitles', {})
                
                audio_path = str(self.storage_path / f'bilibili_{video_id}.mp3')
                
                subtitle_text = ""
                if subtitles:
                    for lang, subs in subtitles.items():
                        if lang in ['zh-CN', 'zh-Hans', 'zh']:
                            for sub in subs:
                                subtitle_text += sub.get('text', '') + "\n"
                
                return {
                    'video_id': video_id,
                    'video_url': url,
                    'title': title,
                    'author': author,
                    'duration': duration,
                    'description': description,
                    'audio_path': audio_path if os.path.exists(audio_path) else None,
                    'subtitle_text': subtitle_text
                }
        except Exception as e:
            print(f"Error downloading Bilibili video: {e}")
            return None
    
    def _extract_bilibili_id(self, url: str) -> str:
        patterns = [
            r'bilibili\.com/video/(BV\w+)',
            r'bilibili\.com/video/av(\d+)',
            r'b23\.tv/(BV\w+)',
            r'b23\.tv/av(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return url.split('/')[-1].split('?')[0]
    
    def search_douyin_videos(self, keyword: str, max_results: int = 10) -> List[Dict]:
        return []
    
    def search_bilibili_videos(self, keyword: str, max_results: int = 10) -> List[Dict]:
        try:
            search_url = f"https://api.bilibili.com/x/web-interface/search/type"
            params = {
                'keyword': keyword,
                'search_type': 'video',
                'page_size': max_results,
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com',
            }
            
            with httpx.Client() as client:
                response = client.get(search_url, params=params, headers=headers, timeout=30)
                data = response.json()
                
            if data.get('code') != 0:
                return []
            
            results = []
            for item in data.get('data', {}).get('result', []):
                results.append({
                    'video_id': str(item.get('aid', '')),
                    'title': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                    'author': item.get('author', ''),
                    'duration': item.get('duration', ''),
                    'play_count': item.get('play', 0),
                    'url': f"https://www.bilibili.com/video/av{item.get('aid', '')}"
                })
            
            return results
        except Exception as e:
            print(f"Error searching Bilibili: {e}")
            return []


class AudioTranscriber:
    def __init__(self):
        self.model_name = settings.WHISPER_MODEL
        self.model = None
    
    def load_model(self):
        if self.model is None:
            import whisper
            self.model = whisper.load_model(self.model_name)
    
    def transcribe(self, audio_path: str) -> str:
        try:
            self.load_model()
            result = self.model.transcribe(audio_path, language='zh')
            return result.get('text', '')
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict]:
        try:
            self.load_model()
            result = self.model.transcribe(audio_path, language='zh', word_timestamps=True)
            
            segments = []
            for segment in result.get('segments', []):
                segments.append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': segment.get('text', '')
                })
            
            return segments
        except Exception as e:
            print(f"Error transcribing with timestamps: {e}")
            return []

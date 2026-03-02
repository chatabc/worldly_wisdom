import os
import tempfile
import asyncio
from typing import Optional, AsyncGenerator
from fastapi import UploadFile, HTTPException
import httpx

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from app.config import settings


class AudioTranscriber:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        
    def load_model(self):
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper is not installed. Run: pip install openai-whisper")
        
        if self.model is None:
            self.model = whisper.load_model(self.model_size)
    
    async def transcribe_file(self, file_path: str, language: str = "zh") -> dict:
        self.load_model()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.model.transcribe(file_path, language=language)
        )
        
        return {
            "text": result.get("text", ""),
            "segments": [
                {
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", "")
                }
                for seg in result.get("segments", [])
            ],
            "language": result.get("language", language)
        }
    
    async def transcribe_chunks(
        self, 
        audio_chunks: AsyncGenerator[bytes, None],
        language: str = "zh"
    ) -> AsyncGenerator[str, None]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
            try:
                async for chunk in audio_chunks:
                    temp_file.write(chunk)
                
                temp_file.close()
                
                result = await self.transcribe_file(temp_path, language)
                yield result["text"]
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


class AudioService:
    def __init__(self):
        self.transcriber = AudioTranscriber(settings.WHISPER_MODEL if hasattr(settings, 'WHISPER_MODEL') else "base")
        self.allowed_types = [
            "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav",
            "audio/webm", "audio/ogg", "audio/m4a", "audio/x-m4a",
            "video/webm"
        ]
    
    async def process_upload(self, file: UploadFile) -> dict:
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported types: {self.allowed_types}"
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_suffix(file.filename)) as temp_file:
            temp_path = temp_file.name
            
            try:
                content = await file.read()
                temp_file.write(content)
                temp_file.close()
                
                result = await self.transcriber.transcribe_file(temp_path)
                
                return {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "transcription": result
                }
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def _get_suffix(self, filename: Optional[str]) -> str:
        if filename:
            if '.' in filename:
                return '.' + filename.rsplit('.', 1)[-1]
        return '.wav'


audio_service = AudioService()

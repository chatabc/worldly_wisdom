from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from typing import Optional
import asyncio
import json
import tempfile
import os

from app.services.audio_service import audio_service
from app.services.llm_service import get_llm_service
from app.services.prompts import ANALYSIS_SYSTEM_PROMPT

router = APIRouter()


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    result = await audio_service.process_upload(file)
    
    return {
        "status": "success",
        "filename": result["filename"],
        "transcription": result["transcription"]["text"],
        "segments": result["transcription"]["segments"],
        "language": result["transcription"]["language"]
    }


@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    audio_result = await audio_service.process_upload(file)
    transcription = audio_result["transcription"]["text"]
    
    llm = get_llm_service()
    analysis = await llm.analyze_text(
        text=transcription,
        system_prompt=ANALYSIS_SYSTEM_PROMPT
    )
    
    return {
        "transcription": transcription,
        "segments": audio_result["transcription"]["segments"],
        "analysis": analysis
    }


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/realtime")
async def websocket_audio(websocket: WebSocket):
    await manager.connect(websocket)
    
    temp_file = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
    temp_path = temp_file.name
    audio_data = b""
    
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_data += data
            
            await websocket.send_text(json.dumps({
                "type": "audio_received",
                "size": len(audio_data)
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
        if audio_data:
            temp_file.write(audio_data)
            temp_file.close()
            
            try:
                result = await audio_service.transcriber.transcribe_file(temp_path)
                
                await manager.broadcast(json.dumps({
                    "type": "transcription_complete",
                    "text": result["text"],
                    "segments": result["segments"]
                }))
            except Exception as e:
                await manager.broadcast(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
        manager.disconnect(websocket)


@router.websocket("/realtime-stream")
async def websocket_audio_stream(websocket: WebSocket):
    await websocket.accept()
    
    buffer = b""
    chunk_count = 0
    
    try:
        while True:
            message = await websocket.receive()
            
            if message["type"] == "websocket.receive":
                if "bytes" in message:
                    audio_chunk = message["bytes"]
                    buffer += audio_chunk
                    chunk_count += 1
                    
                    await websocket.send_text(json.dumps({
                        "type": "chunk_received",
                        "chunk_id": chunk_count,
                        "buffer_size": len(buffer)
                    }))
                    
                elif "text" in message:
                    data = json.loads(message["text"])
                    
                    if data.get("type") == "end_stream":
                        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                            temp_file.write(buffer)
                            temp_path = temp_file.name
                        
                        try:
                            result = await audio_service.transcriber.transcribe_file(temp_path)
                            
                            await websocket.send_text(json.dumps({
                                "type": "transcription_complete",
                                "text": result["text"],
                                "segments": result["segments"]
                            }))
                            
                            if data.get("analyze", False):
                                llm = get_llm_service()
                                analysis = await llm.analyze_text(
                                    text=result["text"],
                                    system_prompt=ANALYSIS_SYSTEM_PROMPT
                                )
                                
                                await websocket.send_text(json.dumps({
                                    "type": "analysis_complete",
                                    "analysis": analysis
                                }))
                                
                        except Exception as e:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": str(e)
                            }))
                        finally:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                        
                        buffer = b""
                        chunk_count = 0
                        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except:
            pass

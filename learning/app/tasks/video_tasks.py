import os
from datetime import datetime
from celery import shared_task
from app.database import SessionLocal
from app.models import LearningTask, LearningKeyword
from app.services.video_service import VideoDownloader, AudioTranscriber
from app.services.knowledge_service import KnowledgeExtractor, KnowledgeStore
from app.config import settings
import asyncio

video_downloader = VideoDownloader()
audio_transcriber = AudioTranscriber()


@shared_task(bind=True, max_retries=3)
def process_video_task(self, task_id: int, platform: str, url: str):
    db = SessionLocal()
    
    try:
        task = db.query(LearningTask).filter(LearningTask.id == task_id).first()
        if not task:
            return {"status": "error", "message": "Task not found"}
        
        task.status = "downloading"
        task.celery_task_id = self.request.id
        db.commit()
        
        if platform == "douyin":
            video_info = video_downloader.download_douyin_video(url)
        elif platform == "bilibili":
            video_info = video_downloader.download_bilibili_video(url)
        else:
            task.status = "failed"
            task.error_message = f"Unsupported platform: {platform}"
            db.commit()
            return {"status": "error", "message": task.error_message}
        
        if not video_info:
            task.status = "failed"
            task.error_message = "Failed to download video"
            db.commit()
            return {"status": "error", "message": task.error_message}
        
        task.video_id = video_info.get('video_id')
        task.video_title = video_info.get('title')
        task.video_author = video_info.get('author')
        task.video_duration = video_info.get('duration')
        task.status = "transcribing"
        db.commit()
        
        content_text = ""
        
        if video_info.get('subtitle_text'):
            content_text = video_info['subtitle_text']
        
        if video_info.get('audio_path') and os.path.exists(video_info['audio_path']):
            task.status = "transcribing_audio"
            db.commit()
            
            transcribed_text = audio_transcriber.transcribe(video_info['audio_path'])
            if transcribed_text:
                content_text = content_text + "\n" + transcribed_text if content_text else transcribed_text
        
        if not content_text.strip():
            task.status = "failed"
            task.error_message = "No content extracted from video"
            db.commit()
            return {"status": "error", "message": task.error_message}
        
        task.extracted_text = content_text
        task.status = "extracting_knowledge"
        db.commit()
        
        extractor = KnowledgeExtractor()
        knowledge_items = asyncio.run(
            extractor.extract_knowledge(
                title=video_info.get('title', ''),
                content=content_text
            )
        )
        
        if knowledge_items:
            store = KnowledgeStore()
            asyncio.run(
                store.store_knowledge(
                    knowledge_items=knowledge_items,
                    source=f"{platform}:{video_info.get('author', '')}",
                    source_url=url
                )
            )
            task.knowledge_extracted = True
        
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "video_id": video_info.get('video_id'),
            "title": video_info.get('title'),
            "knowledge_count": len(knowledge_items)
        }
        
    except Exception as e:
        db.rollback()
        try:
            task = db.query(LearningTask).filter(LearningTask.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_message = str(e)
                db.commit()
        except:
            pass
        
        raise self.retry(exc=e, countdown=60)
    
    finally:
        db.close()


@shared_task
def scheduled_learning():
    if not settings.LEARNING_ENABLED:
        return {"status": "skipped", "message": "Learning is disabled"}
    
    db = SessionLocal()
    
    try:
        keywords = db.query(LearningKeyword).filter(LearningKeyword.is_active == True).all()
        
        if not keywords:
            douyin_keywords = settings.DOUYIN_KEYWORDS.split(',')
            bilibili_keywords = settings.BILIBILI_KEYWORDS.split(',')
            
            for kw in douyin_keywords:
                keyword = LearningKeyword(platform='douyin', keyword=kw.strip())
                db.add(keyword)
            
            for kw in bilibili_keywords:
                keyword = LearningKeyword(platform='bilibili', keyword=kw.strip())
                db.add(keyword)
            
            db.commit()
            keywords = db.query(LearningKeyword).filter(LearningKeyword.is_active == True).all()
        
        tasks_created = 0
        
        for keyword in keywords[:5]:
            if keyword.platform == 'bilibili':
                videos = video_downloader.search_bilibili_videos(keyword.keyword, max_results=3)
                
                for video in videos:
                    existing = db.query(LearningTask).filter(
                        LearningTask.video_id == video['video_id']
                    ).first()
                    
                    if not existing:
                        task = LearningTask(
                            platform='bilibili',
                            keyword=keyword.keyword,
                            video_id=video['video_id'],
                            video_url=video['url'],
                            video_title=video['title'],
                            status='pending'
                        )
                        db.add(task)
                        tasks_created += 1
        
        db.commit()
        
        pending_tasks = db.query(LearningTask).filter(LearningTask.status == 'pending').limit(5).all()
        
        for task in pending_tasks:
            process_video_task.delay(task.id, task.platform, task.video_url)
        
        return {
            "status": "success",
            "tasks_created": tasks_created,
            "tasks_processed": len(pending_tasks)
        }
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@shared_task
def search_and_download_task(platform: str, keyword: str, max_results: int = 5):
    db = SessionLocal()
    
    try:
        videos = []
        
        if platform == 'bilibili':
            videos = video_downloader.search_bilibili_videos(keyword, max_results)
        
        tasks_created = []
        
        for video in videos:
            existing = db.query(LearningTask).filter(
                LearningTask.video_id == video['video_id']
            ).first()
            
            if not existing:
                task = LearningTask(
                    platform=platform,
                    keyword=keyword,
                    video_id=video['video_id'],
                    video_url=video['url'],
                    video_title=video['title'],
                    status='pending'
                )
                db.add(task)
                db.commit()
                
                process_video_task.delay(task.id, platform, video['url'])
                tasks_created.append(task.id)
        
        return {
            "status": "success",
            "videos_found": len(videos),
            "tasks_created": tasks_created
        }
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()

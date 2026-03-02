from celery import shared_task
from app.database import SessionLocal
from app.models import LearningTask
from app.services.knowledge_service import KnowledgeExtractor, KnowledgeStore
import asyncio


@shared_task
def reprocess_failed_tasks():
    db = SessionLocal()
    
    try:
        failed_tasks = db.query(LearningTask).filter(
            LearningTask.status == 'failed',
            LearningTask.extracted_text != None
        ).all()
        
        reprocessed = 0
        
        for task in failed_tasks:
            if task.extracted_text:
                extractor = KnowledgeExtractor()
                knowledge_items = asyncio.run(
                    extractor.extract_knowledge(
                        title=task.video_title or '',
                        content=task.extracted_text
                    )
                )
                
                if knowledge_items:
                    store = KnowledgeStore()
                    asyncio.run(
                        store.store_knowledge(
                            knowledge_items=knowledge_items,
                            source=f"{task.platform}:{task.video_author or ''}",
                            source_url=task.video_url
                        )
                    )
                    
                    task.knowledge_extracted = True
                    task.status = 'completed'
                    reprocessed += 1
        
        db.commit()
        
        return {
            "status": "success",
            "reprocessed": reprocessed
        }
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@shared_task
def get_learning_statistics():
    db = SessionLocal()
    
    try:
        total_tasks = db.query(LearningTask).count()
        completed_tasks = db.query(LearningTask).filter(
            LearningTask.status == 'completed'
        ).count()
        failed_tasks = db.query(LearningTask).filter(
            LearningTask.status == 'failed'
        ).count()
        pending_tasks = db.query(LearningTask).filter(
            LearningTask.status == 'pending'
        ).count()
        
        knowledge_extracted = db.query(LearningTask).filter(
            LearningTask.knowledge_extracted == True
        ).count()
        
        return {
            "status": "success",
            "statistics": {
                "total_tasks": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "pending": pending_tasks,
                "knowledge_extracted": knowledge_extracted,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()

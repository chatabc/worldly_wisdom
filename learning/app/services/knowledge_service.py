import json
import httpx
from typing import List, Dict, Optional
from app.config import settings


KNOWLEDGE_EXTRACTION_PROMPT = """请从以下视频内容中提取社交技巧知识点。

视频标题：{title}
视频内容：
{content}

请提取其中的社交技巧、沟通策略、心理学原理、人情世故等知识点。

以JSON格式返回，格式如下：
{{
    "knowledge_items": [
        {{
            "title": "知识点标题（简洁明了）",
            "content": "知识点详细内容（包含具体场景和应对方法）",
            "category": "分类（职场沟通/情绪管理/谈判技巧/人际关系/领导力/其他）",
            "tags": ["标签1", "标签2"],
            "key_points": ["要点1", "要点2"]
        }}
    ]
}}

注意：
1. 每个知识点要具体、可操作
2. 结合视频中的实际案例
3. 提取通用的社交原则和技巧
4. 标签要简洁准确
"""


class KnowledgeExtractor:
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY or settings.OPENAI_API_KEY
        self.use_qwen = bool(settings.QWEN_API_KEY)
    
    async def extract_knowledge(self, title: str, content: str) -> List[Dict]:
        if not content.strip():
            return []
        
        prompt = KNOWLEDGE_EXTRACTION_PROMPT.format(title=title, content=content[:4000])
        
        try:
            if self.use_qwen:
                return await self._extract_with_qwen(prompt)
            else:
                return await self._extract_with_openai(prompt)
        except Exception as e:
            print(f"Error extracting knowledge: {e}")
            return []
    
    async def _extract_with_qwen(self, prompt: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers={
                    "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-max",
                    "input": {
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    },
                    "parameters": {"temperature": 0.3}
                },
                timeout=60
            )
            
            result = response.json()
            text = result["output"]["choices"][0]["message"]["content"]
            
            return self._parse_knowledge_json(text)
    
    async def _extract_with_openai(self, prompt: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=60
            )
            
            result = response.json()
            text = result["choices"][0]["message"]["content"]
            
            return self._parse_knowledge_json(text)
    
    def _parse_knowledge_json(self, text: str) -> List[Dict]:
        try:
            json_match = text[text.find('{'):text.rfind('}')+1]
            data = json.loads(json_match)
            return data.get('knowledge_items', [])
        except json.JSONDecodeError:
            items = []
            lines = text.split('\n')
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('标题') or line.startswith('知识点'):
                    if current_item:
                        items.append(current_item)
                    current_item = {'title': line.split(':', 1)[-1].strip() if ':' in line else line}
                elif line.startswith('内容') and current_item:
                    current_item['content'] = line.split(':', 1)[-1].strip() if ':' in line else ''
                elif line.startswith('分类') and current_item:
                    current_item['category'] = line.split(':', 1)[-1].strip() if ':' in line else '其他'
            
            if current_item:
                items.append(current_item)
            
            return items


class KnowledgeStore:
    def __init__(self):
        self.chromadb_host = settings.CHROMADB_HOST
    
    async def store_knowledge(self, knowledge_items: List[Dict], source: str, source_url: str):
        import chromadb
        
        client = chromadb.HttpClient(host=self.chromadb_host.replace('http://', '').split(':')[0], 
                                      port=int(self.chromadb_host.split(':')[-1]))
        
        collection = client.get_or_create_collection(name="social_wisdom")
        
        from app.database import SessionLocal
        from app.models import LearningTask
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            for idx, item in enumerate(knowledge_items):
                item_id = f"{source}_{idx}_{hash(item.get('title', ''))}"
                
                collection.add(
                    documents=[item.get('content', '')],
                    metadatas=[{
                        'title': item.get('title', ''),
                        'category': item.get('category', '其他'),
                        'tags': ','.join(item.get('tags', [])),
                        'source': source,
                        'source_url': source_url
                    }],
                    ids=[item_id]
                )
                
                db.execute(text("""
                    INSERT INTO knowledge_items (title, content, category, tags, source, source_url)
                    VALUES (:title, :content, :category, :tags, :source, :source_url)
                """), {
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'category': item.get('category', '其他'),
                    'tags': item.get('tags', []),
                    'source': source,
                    'source_url': source_url
                })
            
            db.commit()
        finally:
            db.close()

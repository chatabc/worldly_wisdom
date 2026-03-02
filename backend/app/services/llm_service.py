from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import httpx
from app.config import settings


class BaseLLMService(ABC):
    @abstractmethod
    async def analyze_text(self, text: str, system_prompt: str) -> str:
        pass

    @abstractmethod
    async def analyze_image(self, image_base64: str, text: Optional[str], system_prompt: str) -> str:
        pass


class MockLLMService(BaseLLMService):
    """模拟LLM服务，用于测试"""
    
    async def analyze_text(self, text: str, system_prompt: str) -> str:
        return '''{
            "real_intent": "说话人希望你能自主决策，但同时也在观察你的判断能力和责任心",
            "metaphors": ["'看着办'表面是授权，实际可能是考验或推卸责任"],
            "emotional_state": "表面平静，内心可能在观察你的反应",
            "attitude": "既期待又保留，给你空间但也留有余地",
            "potential_traps": ["不要以为真的是完全授权", "需要考虑领导的潜在期望", "决策后要及时汇报"]
        }'''
    
    async def analyze_image(self, image_base64: str, text: Optional[str], system_prompt: str) -> str:
        return self.analyze_text(text or "图片内容", system_prompt)


class OpenAIService(BaseLLMService):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def analyze_text(self, text: str, system_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    async def analyze_image(self, image_base64: str, text: Optional[str], system_prompt: str) -> str:
        content = []
        if text:
            content.append({"type": "text", "text": text})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content


class QwenService(BaseLLMService):
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        if not self.api_key:
            raise ValueError("QWEN_API_KEY is not set")
        self.model = settings.QWEN_MODEL
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    async def analyze_text(self, text: str, system_prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": {
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text}
                        ]
                    },
                    "parameters": {"temperature": 0.7}
                }
            )
            result = response.json()
            return result["output"]["choices"][0]["message"]["content"]

    async def analyze_image(self, image_base64: str, text: Optional[str], system_prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-vl-max",
                    "input": {
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": [
                                {"image": f"data:image/jpeg;base64,{image_base64}"},
                                {"text": text or "分析这张图片中的对话内容"}
                            ]}
                        ]
                    }
                }
            )
            result = response.json()
            return result["output"]["choices"][0]["message"]["content"]


class OllamaService(BaseLLMService):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = "qwen2.5:7b"

    async def analyze_text(self, text: str, system_prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": text,
                    "system": system_prompt,
                    "stream": False
                }
            )
            result = response.json()
            return result["response"]

    async def analyze_image(self, image_base64: str, text: Optional[str], system_prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": "llava",
                    "prompt": text or "分析这张图片中的对话内容",
                    "system": system_prompt,
                    "images": [image_base64],
                    "stream": False
                }
            )
            result = response.json()
            return result["response"]


def get_llm_service(provider: Optional[str] = None) -> BaseLLMService:
    provider = provider or settings.DEFAULT_MODEL_PROVIDER
    
    # 如果没有配置任何API Key，使用模拟服务
    has_api_key = (
        (provider == "openai" and settings.OPENAI_API_KEY) or
        (provider == "qwen" and settings.QWEN_API_KEY) or
        (provider == "ollama")
    )
    
    if not has_api_key:
        return MockLLMService()
    
    services = {
        "openai": OpenAIService,
        "qwen": QwenService,
        "ollama": OllamaService
    }
    
    service_class = services.get(provider)
    if not service_class:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    return service_class()

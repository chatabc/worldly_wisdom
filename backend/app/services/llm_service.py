from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import httpx
from openai import AsyncOpenAI
from app.config import settings


class BaseLLMService(ABC):
    @abstractmethod
    async def analyze_text(self, text: str, system_prompt: str) -> str:
        pass

    @abstractmethod
    async def analyze_image(self, image_base64: str, text: Optional[str], system_prompt: str) -> str:
        pass


class OpenAIService(BaseLLMService):
    def __init__(self):
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
    
    services = {
        "openai": OpenAIService,
        "qwen": QwenService,
        "ollama": OllamaService
    }
    
    service_class = services.get(provider)
    if not service_class:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    return service_class()

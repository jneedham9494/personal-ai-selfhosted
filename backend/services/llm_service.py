import ollama
from typing import AsyncGenerator, List, Dict
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)

class LLMService:
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.model = model
        self.system_prompt = """You are a personal AI assistant focused on productivity, self-improvement, and knowledge management.

You have access to the user's Obsidian vault with their personal notes, goals, habit tracking, and journal entries.

Key capabilities:
- Personal task and todo management
- Goal tracking (XRPL learning, Japanese study, fitness)
- Habit tracking and streak monitoring
- Self-reflection and journaling prompts
- Search personal knowledge base
- Proactive nudges and reminders

Be supportive, encouraging, and help the user stay aligned with their personal goals and self-improvement journey."""

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate LLM response with streaming"""

        # Prepare messages
        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *messages
        ]

        try:
            if stream:
                # Stream response - run in thread pool since ollama is synchronous
                def _stream():
                    return ollama.chat(
                        model=self.model,
                        messages=full_messages,
                        stream=True
                    )

                loop = asyncio.get_event_loop()
                response_stream = await loop.run_in_executor(executor, _stream)

                for chunk in response_stream:
                    content = chunk['message']['content']
                    if content:
                        yield content
            else:
                # Non-streaming response - run in thread pool
                def _generate():
                    return ollama.chat(
                        model=self.model,
                        messages=full_messages
                    )

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(executor, _generate)
                yield response['message']['content']

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            yield f"Error: {str(e)}"

    def check_health(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            ollama.list()
            return True
        except Exception:
            return False

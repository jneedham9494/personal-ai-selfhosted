from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import sys
import logging
sys.path.append('..')
from services.llm_service import LLMService
from services.commands import CommandParser
from services.obsidian import ObsidianService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
import os
obsidian_service = ObsidianService()
commands_dir = os.path.join(os.path.dirname(__file__), '../../.ai/commands')
command_parser = CommandParser(commands_dir=commands_dir, obsidian_service=obsidian_service)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False

@router.post("/message")
async def chat_message(request: ChatRequest):
    """Send message to LLM"""

    logger.info(f"Received chat request: {request.model_dump()}")

    # Check if the last message is a slash command
    if request.messages:
        last_message = request.messages[-1]
        if last_message.role == 'user':
            parsed_command = command_parser.parse(last_message.content)

            if parsed_command:
                logger.info(f"Detected command: {parsed_command}")
                result = await command_parser.execute(parsed_command)

                if result['success']:
                    # Special handling for help command
                    if result['message'] == 'help_all':
                        commands = result['data']['commands']
                        response_text = "📚 Available Commands\n\n"
                        for cmd in sorted(commands, key=lambda x: x['name']):
                            response_text += f"/{cmd['name']}\n"
                            response_text += f"  {cmd['description']}\n"
                            response_text += f"  Usage: {cmd['syntax']}\n\n"
                        response_text += "Type /help <command> for more details"
                    elif result['message'] == 'help_specific':
                        cmd_def = result['data']['definition']
                        cmd_name = result['data']['command']
                        response_text = f"📖 Help: /{cmd_name}\n\n"
                        response_text += f"Description: {cmd_def.get('description', 'N/A')}\n"
                        response_text += f"Usage: {cmd_def.get('syntax', 'N/A')}\n\n"
                        if 'examples' in cmd_def and cmd_def['examples']:
                            response_text += "Examples:\n"
                            for example in cmd_def['examples']:
                                response_text += f"  {example}\n"
                    elif result['message'] == 'search_results':
                        # Handle search results
                        search_data = result['data']
                        results = search_data['results']
                        count = search_data['count']

                        response_text = f"🔍 Search Results: {count} matches found\n\n"

                        if count == 0:
                            response_text += "No results found for your query."
                        else:
                            for i, res in enumerate(results[:10], 1):  # Show max 10
                                response_text += f"{i}. {res['file']}\n"
                                response_text += f"   Line {res['line_number']}: {res['excerpt']}\n\n"

                            if count > 10:
                                response_text += f"... and {count - 10} more results"
                    else:
                        # Regular command response
                        response_text = f"✓ Command recognized: /{parsed_command['command']}\n\n"
                        if parsed_command['definition']:
                            response_text += f"{parsed_command['definition'].get('description', '')}\n\n"
                        response_text += f"Arguments: {parsed_command['args'] or 'none'}\n\n"
                        response_text += "Note: Full command execution coming soon!"
                else:
                    response_text = f"✗ {result['message']}"

                return {"response": response_text}

    llm = LLMService()

    # Convert messages to dict format
    messages_dict = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    logger.info(f"Converted messages: {messages_dict}")

    if request.stream:
        async def generate():
            async for chunk in llm.generate_response(messages_dict, stream=True):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )
    else:
        # Non-streaming response
        response_parts = []
        async for chunk in llm.generate_response(messages_dict, stream=False):
            response_parts.append(chunk)

        return {"response": "".join(response_parts)}

@router.get("/health")
async def chat_health():
    """Check if LLM is accessible"""
    llm = LLMService()
    healthy = llm.check_health()

    if not healthy:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    return {"status": "healthy", "model": "qwen2.5-coder:7b"}

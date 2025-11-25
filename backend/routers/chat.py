from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx
import json
import os
import re
from typing import Optional

from routers.models import ChatRequest, ChatResponse
from routers.utils import extract_thinking_from_content

router = APIRouter(prefix="/chat", tags=["chat"])

# URL Ollama (работает с Docker контейнером на localhost:11434)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Отправляет запрос в Ollama и возвращает мышление и ответ
    """
    ollama_url = f"{OLLAMA_URL}/api/chat"
    
    payload = {
        "model": request.model,
        "messages": [
            {
                "role": "user",
                "content": request.message
            }
        ],
        "stream": True
    }
    
    thinking_parts = []
    response_parts = []
    error_message = None
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", ollama_url, json=payload) as response:
                # Проверяем статус ответа
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_message = f"Ollama API error {response.status_code}: {error_text.decode()}"
                else:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                
                                # Проверяем наличие ошибки в ответе
                                if "error" in data:
                                    error_message = data.get("error", "Unknown error")
                                    break
                                
                                # Извлекаем мышление (если есть в ответе)
                                # Проверяем наличие поля thinking в ответе
                                if "thinking" in data:
                                    thinking_content = data.get("thinking", "")
                                    if thinking_content:
                                        thinking_parts.append(thinking_content)
                                
                                # Проверяем наличие thinking в message
                                if "message" in data:
                                    message = data["message"]
                                    
                                    # Проверяем поле thinking в message
                                    if "thinking" in message:
                                        thinking_content = message.get("thinking", "")
                                        if thinking_content:
                                            thinking_parts.append(thinking_content)
                                    
                                    # Извлекаем content
                                    content = message.get("content", "")
                                    
                                    # Проверяем, есть ли мышление в XML-тегах
                                    if content:
                                        thinking_from_content, cleaned_content = extract_thinking_from_content(content)
                                        if thinking_from_content:
                                            thinking_parts.append(thinking_from_content)
                                        if cleaned_content:
                                            response_parts.append(cleaned_content)
                                
                                # Проверяем, завершен ли ответ
                                if data.get("done", False):
                                    break
                                    
                            except json.JSONDecodeError as e:
                                # Логируем проблему с парсингом, но продолжаем
                                print(f"JSON decode error: {e}, line: {line}")
                                continue
    except httpx.RequestError as e:
        error_message = f"Connection error: {str(e)}"
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
    
    thinking = "".join(thinking_parts) if thinking_parts else None
    response_text = "".join(response_parts)
    
    # Если есть ошибка или пустой ответ, возвращаем сообщение об ошибке
    if error_message:
        response_text = error_message
    elif not response_text:
        response_text = "Пустой ответ от Ollama. Убедитесь, что модель установлена: docker exec -it ollama ollama pull llama3.2"
    
    return ChatResponse(
        thinking=thinking,
        response=response_text
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Стриминг версия для получения ответа по частям
    """
    ollama_url = f"{OLLAMA_URL}/api/chat"
    
    payload = {
        "model": request.model,
        "messages": [
            {
                "role": "user",
                "content": request.message
            }
        ],
        "stream": True
    }
    
    async def generate():
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", ollama_url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            
                            # Извлекаем thinking если есть
                            thinking_content = None
                            if "thinking" in data:
                                thinking_content = data.get("thinking", "")
                            
                            if "message" in data:
                                content = data["message"].get("content", "")
                                done = data.get("done", False)
                                
                                result = {
                                    "content": content,
                                    "thinking": None,  # В стриминге thinking обрабатывается отдельно
                                    "done": done
                                }
                                
                                yield f"data: {json.dumps(result)}\n\n"
                                
                                if done:
                                    break
                                    
                        except json.JSONDecodeError:
                            continue
    
    return StreamingResponse(generate(), media_type="text/event-stream")


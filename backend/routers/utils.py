import re

def extract_thinking_from_content(content: str) -> tuple[str, str]:
    """
    Извлекает thinking из контента и возвращает (thinking, cleaned_content)
    """
    thinking_parts = []
    
    # Ищем теги <think>...</think>
    think_pattern = r'<think[^>]*>(.*?)</think>'
    think_matches = re.findall(think_pattern, content, re.DOTALL | re.IGNORECASE)
    if think_matches:
        thinking_parts.extend(think_matches)
        # Удаляем thinking теги из content
        content = re.sub(think_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Проверяем специальные маркеры для reasoning моделей
    if "reasoning" in content.lower() or "let me think" in content.lower():
        if len(thinking_parts) == 0 and len(content) > 100:
            # Пытаемся разделить thinking и ответ
            parts = re.split(r'(?i)(?:final answer|answer:|ответ:)', content, maxsplit=1)
            if len(parts) > 1:
                thinking_parts.append(parts[0].strip())
                content = parts[1].strip() if parts[1] else content
    
    thinking = "".join(thinking_parts) if thinking_parts else None
    return thinking, content.strip()

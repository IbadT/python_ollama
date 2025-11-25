# Ollama Chat Application

Чат-приложение с AI на базе Ollama. Фронтенд на React, бэкенд на FastAPI.

## Требования

- Python 3.8+
- Node.js 18+
- Docker и Docker Compose (для запуска Ollama)

## Установка и запуск

### Бэкенд

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

**Отключение от виртуального окружения:**
```bash
deactivate
```

Бэкенд будет доступен на `http://localhost:8000`

### Фронтенд

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен на `http://localhost:5173`

## Использование

### 1. Запуск Ollama в Docker

```bash
cd config
docker compose up -d
```

Это запустит Ollama контейнер на `localhost:11434`. Модели будут сохраняться в Docker volume.

### 2. Установка модели в Ollama

После запуска контейнера, установите модель:

```bash
docker exec -it ollama ollama pull llama3.2
```

Или любую другую модель:
```bash
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull gemma2
```

### 3. Запуск бэкенда

```bash
cd backend
source venv/bin/activate  # Активация виртуального окружения
python3 main.py
```

**Отключение от виртуального окружения:**
```bash
deactivate
```

### 4. Запуск фронтенда

```bash
cd frontend
npm run dev
```

### 5. Использование

Откройте браузер на `http://localhost:5173` и начните чат!

### Остановка Ollama

```bash
cd config
docker compose down
```

Для полной очистки (включая модели):
```bash
docker compose down -v
```

## API Endpoints

- `POST /chat` - Отправка сообщения и получение ответа с мышлением
- `POST /chat/stream` - Стриминг версия (SSE)


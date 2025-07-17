# Техническая Документация - XOFlowers AI Agent

## 📋 Детальное Описание Компонентов

### 1. Главный Файл - `main.py`

**Роль**: Единая точка входа в приложение
**Функционал**:

- Парсинг командной строки с аргументами `--platform`, `--port`, `--debug`
- Валидация наличия `.env` файла
- Запуск соответствующего бота (Telegram/Instagram)
- Graceful shutdown при Ctrl+C
- Обработка исключений

**Пример использования**:

```bash
python main.py --platform telegram --debug  # Telegram с отладкой
python main.py --platform instagram --port 5001  # Instagram на порту 5001
```

### 2. API Интерфейсы (`src/api/`)

#### 2.1 Telegram Bot (`telegram_app.py`)

```python
class XOFlowersTelegramBot:
    def __init__(self):
        # Инициализация с токеном из .env
        # Создание Application builder
        # Настройка handlers

    async def handle_message(self, update, context):
        # Фильтрация через SecurityFilter
        # Передача в ConversationManager
        # Отправка ответа пользователю
```

**Поддерживаемые команды**:

- `/start` - Приветствие и инициализация
- `/help` - Справочная информация
- `/contact` - Контактные данные

#### 2.2 Instagram Bot (`instagram_app.py`)

```python
class XOFlowersInstagramBot:
    def __init__(self, debug=False):
        # Flask приложение для webhook
        # Настройка маршрутов

    def verify_webhook(self):
        # Верификация Meta webhook

    def handle_webhook(self):
        # Обработка входящих сообщений
        # Парсинг JSON payload
```

### 3. Интеллектуальный Движок (`src/intelligence/`)

#### 3.1 Центральный Менеджер (`conversation_manager.py`)

```python
class ConversationManager:
    def __init__(self):
        self.ai_engine = get_ai_engine()
        self.search_engine = get_search_engine()
        self.context_manager = get_context_manager()
        self.chromadb_manager = get_chromadb_manager()

    def process_message_sync(self, user_id: str, message: str) -> str:
        # 1. Загрузка контекста пользователя
        # 2. Обогащение сообщения контекстом
        # 3. Поиск релевантных продуктов
        # 4. Генерация ответа через ИИ
        # 5. Сохранение контекста
```

#### 3.2 ИИ Движок (`ai_conversation_engine.py`)

```python
class AIConversationEngine:
    def __init__(self):
        self.openai_client = OpenAI()  # Основной
        self.gemini_client = genai.GenerativeModel()  # Резервный

    async def generate_response(self, enhanced_message: str) -> str:
        # Попытка через OpenAI
        # При неудаче - fallback на Gemini
        # Обработка ошибок и retry логика
```

#### 3.3 Поиск Продуктов (`product_search.py`)

```python
class ProductSearchEngine:
    def search_products(self, query: str, limit: int = 5) -> List[Dict]:
        # Векторный поиск через ChromaDB
        # Фильтрация по релевантности
        # Форматирование результатов
```

#### 3.4 ChromaDB Менеджер (`chromadb_manager.py`)

```python
class ChromaDBManager:
    def __init__(self):
        # Инициализация 5 коллекций:
        # - products_main (общие продукты)
        # - products_bouquets (букеты)
        # - products_boxes (коробки)
        # - products_plants (растения)
        # - products_occasions (тематические)

    def search_across_collections(self, query: str) -> List[Dict]:
        # Поиск по всем коллекциям
        # Объединение и ранжирование результатов
```

#### 3.5 Управление Контекстом (`conversation_context.py`)

```python
class ConversationContext:
    def load_context(self, user_id: str) -> Dict:
        # Загрузка из data/user_{user_id}.json
        # Инициализация при отсутствии

    def save_context(self, user_id: str, context: Dict):
        # Сохранение истории и предпочтений
        # Управление размером контекста
```

### 4. Система Поиска (`src/database/`)

#### 4.1 Векторный Поиск (`chromadb_search_engine.py`)

```python
class XOFlowersSearchEngine:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path="./chroma_db")

    def search(self, query: str, category: str = None) -> List[Dict]:
        # Векторизация запроса
        # Поиск по similarity
        # Фильтрация по категориям
        # Возврат топ результатов
```

**Структура данных продуктов**:

```json
{
  "name": "Букет 'Нежность'",
  "description": "Романтический букет из белых роз",
  "price": "850 MDL",
  "category": "Classic Bouquets",
  "url": "https://xoflowers.md/product/tenderness",
  "language": "russian"
}
```

### 5. Безопасность (`src/security/`)

#### 5.1 Фильтры (`filters.py`)

```python
class SecurityFilter:
    def filter_message(self, message: str) -> str:
        # Удаление потенциально опасного контента
        # Валидация длины сообщения
        # Проверка на спам-паттерны

    def is_valid_user(self, user_id: str) -> bool:
        # Проверка black list
        # Rate limiting
```

### 6. Конфигурация (`config/settings.py`)

```python
# Настройки ИИ моделей
AI_MODEL = {
    'primary': 'openai',
    'fallback': 'gemini',
    'temperature': 0.7,
    'max_tokens': 1000
}

# Настройки базы данных
DATABASE = {
    'chromadb_path': './chroma_db_flowers',
    'embedding_model': 'all-MiniLM-L6-v2',
    'collections': {...}
}

# API конфигурация
API_CONFIG = {
    'instagram': {'webhook_port': 5001},
    'telegram': {'polling_interval': 1.0}
}
```

## 🔄 Жизненный Цикл Запроса

### Пример: Поиск букета роз

1. **Пользователь**: "Хочу букет красных роз на день рождения"

2. **API Layer**:

   ```python
   # telegram_app.py
   message = update.message.text
   user_id = str(update.effective_user.id)
   ```

3. **Security Filter**:

   ```python
   # filters.py
   filtered_message = security_filter.filter_message(message)
   ```

4. **Conversation Manager**:

   ```python
   # conversation_manager.py
   context = context_manager.load_context(user_id)
   enhanced_message = f"{context}\nПользователь: {message}"
   ```

5. **Product Search**:

   ```python
   # product_search.py
   products = search_engine.search_products("красные розы день рождения")
   ```

6. **ChromaDB Query**:

   ```python
   # chromadb_search_engine.py
   results = collection.query(
       query_texts=["красные розы день рождения"],
       n_results=5
   )
   ```

7. **AI Response Generation**:

   ```python
   # ai_conversation_engine.py
   prompt = f"""Пользователь ищет: {message}
   Найденные продукты: {products}
   Ответь естественно и предложи лучшие варианты."""

   response = openai_client.chat.completions.create(...)
   ```

8. **Context Save**:

   ```python
   # conversation_context.py
   context_manager.add_message(user_id, message, response)
   ```

9. **Response Delivery**:
   ```python
   # telegram_app.py
   await update.message.reply_text(response)
   ```

## 📊 Метрики и Мониторинг

### Логирование

```python
import logging

# Уровни логирования
logger.info("💬 Processing message")     # Основные события
logger.debug("🔍 Search query: {query}") # Отладка
logger.warning("⚠️ Fallback to Gemini")  # Предупреждения
logger.error("❌ API error: {error}")    # Ошибки
```

### Ключевые Метрики

- **Response Time**: Время ответа на запрос
- **Search Quality**: Релевантность найденных продуктов
- **Conversion Rate**: Переход от поиска к покупке
- **User Satisfaction**: Обратная связь пользователей

## 🔧 Настройка и Отладка

### Режим Отладки

```bash
python main.py --platform telegram --debug
```

**В режиме отладки**:

- Подробное логирование всех операций
- Стектрейсы при ошибках
- Вывод промежуточных результатов
- Сохранение debug информации

### Переменные Окружения

```env
# Обязательные
TELEGRAM_BOT_TOKEN=1234567890:ABC...
OPENAI_API_KEY=sk-...

# Опциональные
GEMINI_API_KEY=AI...
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Структура Логов

```
[2025-01-17 10:30:15] INFO:conversation_manager: 💬 Processing message from user 12345
[2025-01-17 10:30:15] DEBUG:product_search: 🔍 Search query: "красные розы"
[2025-01-17 10:30:16] INFO:chromadb_manager: ✅ Found 5 relevant products
[2025-01-17 10:30:17] INFO:ai_conversation_engine: 🤖 Generated response (156 tokens)
```

## 🚀 Производительность

### Оптимизации

- **Векторный кэш**: Переиспользование эмбеддингов
- **Context pooling**: Эффективное управление памятью
- **Async processing**: Неблокирующие операции
- **Connection pooling**: Оптимизация API вызовов

### Масштабирование

```python
# Будущие улучшения
- Redis для кэширования
- PostgreSQL для аналитики
- Docker контейнеризация
- Kubernetes оркестрация
- Load balancing
```

## 🎯 Лучшие Практики

### Разработка

1. **Модульность**: Каждый компонент независим
2. **Типизация**: Использование type hints
3. **Тестирование**: Покрытие всех ключевых функций
4. **Документация**: Inline комментарии и docstrings

### Безопасность

1. **Валидация входов**: Все пользовательские данные
2. **Rate limiting**: Защита от злоупотреблений
3. **Логирование**: Отслеживание подозрительной активности
4. **Secrets management**: Безопасное хранение ключей

### Надежность

1. **Error handling**: Graceful degradation
2. **Fallback mechanisms**: Резервные пути
3. **Monitoring**: Отслеживание здоровья системы
4. **Backups**: Регулярное сохранение данных

# XOFlowers AI Agent - Архитектура Проекта

## 🌸 Обзор Проекта

XOFlowers AI Agent - это интеллектуальный многоплатформенный чат-бот для цветочного магазина XOFlowers, который обрабатывает запросы клиентов через Instagram и Telegram с использованием передовых технологий ИИ и векторного поиска.

## 🏗️ Архитектура Системы

### Модульная Архитектура

Проект построен по модульному принципу с четким разделением ответственности:

```
flower-chat-agent/
├── main.py                 # Точка входа в приложение
├── src/                    # Основной код приложения
│   ├── api/               # API интерфейсы
│   ├── intelligence/      # ИИ движок и логика
│   ├── database/          # Система поиска и БД
│   └── security/          # Фильтры безопасности
├── config/                # Конфигурация системы
├── data/                  # Данные продуктов
├── tests/                 # Тестовые файлы
└── docs/                  # Документация
```

## 📋 Описание Компонентов

### 1. Точка Входа (`main.py`)

**Назначение**: Центральная точка запуска приложения
**Функции**:

- Парсинг аргументов командной строки
- Выбор платформы (Instagram/Telegram/Both)
- Инициализация соответствующего бота
- Обработка ошибок и graceful shutdown

**Параметры запуска**:

```bash
python main.py --platform telegram        # Только Telegram
python main.py --platform instagram       # Только Instagram
python main.py --platform both           # Обе платформы (в разработке)
python main.py --port 5001 --debug       # С отладкой на порту 5001
```

### 2. API Слой (`src/api/`)

#### 2.1 Telegram Bot (`telegram_app.py`)

**Класс**: `XOFlowersTelegramBot`
**Функции**:

- Обработка команд: `/start`, `/help`, `/contact`
- Обработка текстовых сообщений
- Интеграция с Conversation Manager
- Фильтрация безопасности
- Асинхронная обработка

#### 2.2 Instagram Bot (`instagram_app.py`)

**Класс**: `XOFlowersInstagramBot`
**Функции**:

- Webhook обработка Instagram сообщений
- HTTP сервер на Flask
- Верификация webhook'ов
- Обработка различных типов сообщений

### 3. Интеллектуальный Слой (`src/intelligence/`)

#### 3.1 Conversation Manager (`conversation_manager.py`)

**Класс**: `ConversationManager`
**Роль**: Центральный оркестратор всех компонентов
**Функции**:

- Координация между ИИ движком и поиском
- Управление контекстом разговоров
- Синхронная и асинхронная обработка
- Интеграция всех систем

#### 3.2 AI Conversation Engine (`ai_conversation_engine.py`)

**Класс**: `AIConversationEngine`
**Функции**:

- Интеграция с OpenAI GPT
- Поддержка Google Gemini (fallback)
- Генерация естественных ответов
- Обработка многоязычности (RU/RO/EN)

#### 3.3 Product Search (`product_search.py`)

**Класс**: `ProductSearchEngine`
**Функции**:

- Умный поиск по каталогу
- Семантический поиск продуктов
- Фильтрация по категориям
- Ранжирование результатов

#### 3.4 ChromaDB Manager (`chromadb_manager.py`)

**Класс**: `ChromaDBManager`
**Функции**:

- Управление векторными коллекциями
- Организация продуктов по категориям
- Эмбеддинги и индексация
- Многоязычный поиск

#### 3.5 Context Manager (`conversation_context.py`)

**Класс**: `ConversationContext`
**Функции**:

- Хранение истории разговоров
- Персистентность контекста
- Управление пользовательскими сессиями
- Память о предпочтениях

#### 3.6 Intent Classifier (`intent_classifier.py`)

**Функции**:

- Классификация намерений пользователя
- Определение типа запроса
- Роутинг к соответствующим обработчикам

#### 3.7 Prompts (`prompts.py`)

**Функции**:

- Централизованное управление промптами
- Многоязычные шаблоны
- Системные инструкции для ИИ

### 4. Слой Данных (`src/database/`)

#### 4.1 ChromaDB Search Engine (`chromadb_search_engine.py`)

**Класс**: `XOFlowersSearchEngine`
**Функции**:

- Высокопроизводительный векторный поиск
- Поддержка нескольких языков
- Категоризация продуктов
- Semantic similarity search

**Коллекции**:

- `products_main` - Основные продукты
- `products_bouquets` - Букеты
- `products_boxes` - Коробки с цветами
- `products_plants` - Растения
- `products_occasions` - Тематические композиции

### 5. Безопасность (`src/security/`)

#### 5.1 Security Filters (`filters.py`)

**Класс**: `SecurityFilter`
**Функции**:

- Фильтрация нежелательного контента
- Защита от спама
- Валидация входных данных
- Rate limiting

### 6. Конфигурация (`config/`)

#### 6.1 Settings (`settings.py`)

**Функции**:

- Центральная конфигурация всех компонентов
- Параметры ИИ моделей
- Настройки БД и API
- Константы системы

### 7. Данные (`data/`)

**Файлы**:

- `final_products_case_standardized.csv` - Каталог продуктов
- `faq_data.json` - Часто задаваемые вопросы
- `contexts.json` - Контексты разговоров
- `profiles.json` - Профили пользователей
- `user_*.json` - Индивидуальные данные пользователей

## 🔄 Поток Обработки Сообщений

### 1. Получение Сообщения

```
Telegram/Instagram → API Layer (telegram_app.py/instagram_app.py)
```

### 2. Фильтрация Безопасности

```
API Layer → Security Filter → Validation
```

### 3. Обработка Разговора

```
Security Filter → Conversation Manager → Context Loading
```

### 4. Анализ Намерений

```
Conversation Manager → Intent Classifier → Intent Detection
```

### 5. Поиск Продуктов

```
Intent Classifier → Product Search → ChromaDB Query
```

### 6. Генерация Ответа

```
Product Search → AI Engine → Natural Response Generation
```

### 7. Отправка Ответа

```
AI Engine → Conversation Manager → API Layer → User
```

## 🛠️ Технологический Стек

### Backend

- **Python 3.8+** - Основной язык
- **AsyncIO** - Асинхронная обработка
- **Flask** - HTTP сервер для Instagram
- **python-telegram-bot** - Telegram интеграция

### AI & ML

- **OpenAI GPT** - Основной ИИ движок
- **Google Gemini** - Резервный ИИ
- **ChromaDB** - Векторная база данных
- **SentenceTransformers** - Эмбеддинги
- **all-MiniLM-L6-v2** - Модель для векторизации

### Data & Storage

- **JSON** - Конфигурация и данные пользователей
- **CSV** - Каталог продуктов
- **SQLite** - ChromaDB backend

## 🚀 Развертывание и Запуск

### Требования

```bash
pip install -r requirements.txt
```

### Переменные Окружения

```bash
TELEGRAM_BOT_TOKEN=your_telegram_token
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key (опционально)
INSTAGRAM_VERIFY_TOKEN=your_instagram_token
INSTAGRAM_ACCESS_TOKEN=your_access_token
```

### Запуск

```bash
# Telegram бот
python main.py --platform telegram

# Instagram бот
python main.py --platform instagram --port 5001

# Режим отладки
python main.py --platform telegram --debug
```

## 🧪 Тестирование

### Структура Тестов

```
tests/
├── test_chromadb_system.py    # Тесты векторного поиска
├── test_conversation.py       # Тесты менеджера разговоров
├── test_telegram.py          # Тесты Telegram бота
└── test_urls.py              # Тесты генерации URL
```

### Запуск Тестов

```bash
# Отдельный тест
python tests/test_conversation.py

# Все тесты
python -m pytest tests/
```

## 📊 Мониторинг и Логирование

### Logging

- **INFO** - Основные события системы
- **DEBUG** - Детальная отладочная информация
- **WARNING** - Предупреждения и нестандартные ситуации
- **ERROR** - Ошибки обработки

### Метрики

- Время ответа на запросы
- Качество поиска продуктов
- Удовлетворенность пользователей
- Использование ресурсов

## 🔮 Будущие Улучшения

### Планируемые Функции

- **Режим "both"** - Одновременная работа на обеих платформах
- **Аналитика** - Подробная статистика взаимодействий
- **A/B тестирование** - Оптимизация промптов
- **Персонализация** - Индивидуальные рекомендации
- **Интеграция платежей** - Прямые покупки через бота

### Масштабирование

- **Docker** контейнеризация
- **Kubernetes** оркестрация
- **Redis** для кэширования
- **PostgreSQL** для аналитики
- **Load Balancing** для высоких нагрузок

## 📝 Заключение

XOFlowers AI Agent представляет собой современное решение для автоматизации обслуживания клиентов в цветочной индустрии, сочетающее передовые технологии ИИ с практическими потребностями бизнеса. Модульная архитектура обеспечивает гибкость развития, а использование векторного поиска гарантирует высокое качество рекомендаций продуктов.

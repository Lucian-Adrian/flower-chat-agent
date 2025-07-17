# 📚 Документация XOFlowers AI Agent

Добро пожаловать в центр документации XOFlowers AI Agent - интеллектуального многоплатформенного чат-бота для цветочного магазина.

## 🎯 Быстрый Старт

### Основные Документы

- **[Архитектура Проекта](project_architecture.md)** 📋 - Полное описание системы
- **[Технические Детали](technical_details.md)** 🔧 - Детальная документация API
- **[Развертывание](deployment.md)** 🚀 - Инструкции по установке
- **[Системный Поток](system_flow.md)** 🔄 - Диаграммы и процессы

### Специализированные Руководства

- **[ChromaDB Система](CHROMADB_SYSTEM.md)** 🔍 - Векторная база данных
- **[Интеграция](INTEGRATION_GUIDE.md)** 🔗 - Подключение внешних сервисов

## 📊 Структура Проекта

```
XOFlowers AI Agent
├── 🚀 main.py                    # Точка входа
├── 📱 src/api/                   # API интерфейсы
│   ├── telegram_app.py           # Telegram Bot
│   └── instagram_app.py          # Instagram Bot
├── 🧠 src/intelligence/          # ИИ движок
│   ├── conversation_manager.py   # Центральный оркестратор
│   ├── ai_conversation_engine.py # OpenAI/Gemini
│   ├── product_search.py        # Поиск продуктов
│   └── chromadb_manager.py      # Векторная БД
├── 💾 src/database/             # Система данных
├── 🔒 src/security/             # Безопасность
├── ⚙️ config/                   # Конфигурация
├── 📊 data/                     # Данные продуктов
└── 🧪 tests/                    # Тестирование
```

## 🛠️ Технологический Стек

### Backend & AI

- **Python 3.8+** с AsyncIO
- **OpenAI GPT** + Google Gemini
- **ChromaDB** для векторного поиска
- **SentenceTransformers** для эмбеддингов

### Платформы

- **Telegram Bot API** с python-telegram-bot
- **Instagram Messaging API** с Flask webhooks
- **Multi-platform** архитектура

## 🔄 Поток Работы Системы

1. **Получение сообщения** → API Layer
2. **Фильтрация безопасности** → Security Layer
3. **Анализ намерений** → Intelligence Layer
4. **Поиск продуктов** → ChromaDB Vector Search
5. **Генерация ответа** → AI Engine (OpenAI/Gemini)
6. **Отправка ответа** → User Interface

## 🚀 Быстрые Команды

### Запуск Ботов

```bash
# Telegram бот
python main.py --platform telegram

# Instagram бот
python main.py --platform instagram --port 5001

# Режим отладки
python main.py --platform telegram --debug
```

### Тестирование

```bash
# Отдельный тест
python tests/test_conversation.py

# Все тесты
python -m pytest tests/
```

## 📋 Чек-лист Настройки

### 1. Установка Зависимостей

```bash
pip install -r requirements.txt
```

### 2. Переменные Окружения (.env)

```env
TELEGRAM_BOT_TOKEN=your_token
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key (опционально)
INSTAGRAM_ACCESS_TOKEN=your_token
```

### 3. Инициализация Данных

- ✅ `data/final_products_case_standardized.csv` - каталог продуктов
- ✅ `chroma_db_flowers/` - векторная база данных
- ✅ `config/settings.py` - конфигурация

### 4. Проверка Работоспособности

```bash
python tests/test_chromadb_system.py  # Тест поиска
python tests/test_conversation.py     # Тест ИИ
```

## 🧪 Разработка и Отладка

### Структура Тестов

```
tests/
├── test_chromadb_system.py    # Векторный поиск
├── test_conversation.py       # Менеджер разговоров
├── test_telegram.py          # Telegram интеграция
└── test_urls.py              # URL генерация
```

### Логирование

- **INFO** - Основные события
- **DEBUG** - Детальная отладка (--debug)
- **WARNING** - Предупреждения
- **ERROR** - Ошибки с трассировкой

## 📈 Производительность

### Оптимизации

- **Векторный кэш** для эмбеддингов
- **Асинхронная обработка** сообщений
- **Connection pooling** для API
- **Context management** для памяти

### Метрики

- Время ответа: ~2-3 секунды
- Точность поиска: >85%
- Поддержка языков: RU/RO/EN
- Concurrent users: 100+

## 🔮 Roadmap

### Текущая Версия (v1.0)

- ✅ Telegram/Instagram боты
- ✅ Векторный поиск продуктов
- ✅ Многоязычность (RU/RO/EN)
- ✅ OpenAI + Gemini интеграция

### Планируемые Обновления

- 🔄 Режим "both platforms"
- 📊 Аналитика и метрики
- 💳 Интеграция платежей
- 🎯 Персонализация рекомендаций
- 🐳 Docker контейнеризация

## 🆘 Поддержка

### Частые Проблемы

1. **Ошибка токена** → Проверить `.env` файл
2. **ChromaDB не найдена** → Запустить инициализацию БД
3. **API лимиты** → Проверить квоты OpenAI/Gemini
4. **Медленный поиск** → Оптимизировать размер коллекций

### Контакты

- **GitHub Issues** - для багов и предложений
- **Documentation** - текущая папка `/docs`
- **Testing** - папка `/tests` с примерами

---

**Последнее обновление**: 17 января 2025  
**Версия документации**: 2.0  
**Статус проекта**: ✅ Активная разработка

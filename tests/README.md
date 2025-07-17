# Тесты

Эта папка содержит все тестовые файлы проекта.

## Описание тестов

- `test_chromadb_system.py` - Тесты системы ChromaDB
- `test_conversation.py` - Тесты менеджера разговоров
- `test_telegram.py` - Тесты Telegram бота
- `test_urls.py` - Тесты отображения URL

## Запуск тестов

Для запуска отдельного теста:

```bash
python tests/test_conversation.py
```

Для запуска всех тестов:

```bash
python -m pytest tests/
```

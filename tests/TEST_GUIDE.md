# 🧪 XOFlowers Testing Guide

## Test Structure

```
tests/
├── integration/           # Integration tests
│   ├── test_logging.py   # Logging functionality tests
│   ├── test_openai.py    # OpenAI API integration tests
│   └── test_xoflowers_ai.py  # Complete AI system tests
├── unit/                 # Unit tests
│   ├── test_*.py         # Individual component tests
│   └── data/             # Test data files
└── README.md            # This file
```

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Individual Test Categories
```bash
# Integration tests
python tests/integration/test_logging.py
python tests/integration/test_openai.py
python tests/integration/test_xoflowers_ai.py

# Unit tests
python tests/unit/test_action_handler.py
python tests/unit/test_intent_classifier.py
```

### Run Specific Test Files
```bash
# From project root
python -m pytest tests/unit/test_action_handler.py -v
python -m pytest tests/integration/ -v
```

## Test Categories

### 🔍 Integration Tests
- **test_logging.py**: Tests logging functionality across all components
- **test_openai.py**: Tests OpenAI API integration and authentication
- **test_xoflowers_ai.py**: Tests complete AI system with realistic scenarios

### 🧩 Unit Tests
- **test_action_handler.py**: Tests individual action handlers
- **test_intent_classifier.py**: Tests intent classification logic
- **test_product_search.py**: Tests product search functionality
- **test_*.py**: Other component-specific tests

## Test Data
- Located in `tests/unit/data/`
- Contains sample messages, expected responses, and test fixtures

## Best Practices

1. **Run tests before commits**: `python run_tests.py`
2. **Add tests for new features**: Create corresponding test files
3. **Keep tests focused**: Each test should test one specific functionality
4. **Use descriptive names**: Test names should clearly describe what they test
5. **Include edge cases**: Test both success and failure scenarios

## Logging During Tests
- Tests capture and verify logging output
- Use `logging.INFO` level for detailed test output
- Check that intent classification logs are working correctly

## Environment Setup
Make sure you have:
- Virtual environment activated
- `.env` file with API keys
- All dependencies installed (`pip install -r requirements.txt`)

## Common Issues
- **Import errors**: Make sure `src/` is in Python path
- **Missing API keys**: Check `.env` file has `OPENAI_API_KEY` and `GEMINI_API_KEY`
- **Module not found**: Run from project root directory

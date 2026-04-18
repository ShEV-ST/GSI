# AI Agent Project

Структура проекта для разработки ИИ агента.

## Структура проекта

```
├── src/            # Исходный код агента
├── tests/          # Тесты
├── config/         # Конфигурационные файлы
├── docs/           # Документация
├── scripts/        # Скрипты для запуска и утилиты
├── requirements.txt# Зависимости Python
└── README.md       # Этот файл
```

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

1. Скопируйте `.env.example` в `.env`
2. Заполните необходимые переменные окружения (API ключи и т.д.)

## Запуск

```bash
python -m src.main
```

## Тестирование

```bash
pytest tests/
```

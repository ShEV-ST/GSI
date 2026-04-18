"""Точка входа для ИИ агента."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import Agent


def main():
    """Запуск ИИ агента."""
    agent = Agent()
    
    # Запуск основного цикла через генератор
    try:
        for result in agent.run():
            # Здесь можно обрабатывать результаты выполнения навыков
            pass
    except KeyboardInterrupt:
        print("\nПринудительная остановка агентa.")
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")


if __name__ == "__main__":
    main()

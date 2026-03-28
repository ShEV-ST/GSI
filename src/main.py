"""Точка входа для ИИ агента."""

from src.agent import Agent


def main():
    """Запуск ИИ агента."""
    agent = Agent()
    agent.run()


if __name__ == "__main__":
    main()

"""Основной модуль ИИ агента."""

from dotenv import load_dotenv
import os

load_dotenv()


class Agent:
    """Базовый класс ИИ агента."""

    def __init__(self):
        """Инициализация агента."""
        self.name = os.getenv("AGENT_NAME", "ai_agent")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

    def run(self):
        """Запуск основного цикла агента."""
        print(f"Запуск {self.name}...")
        if self.debug:
            print("Режим отладки включён")
        print("Агент готов к работе.")


if __name__ == "__main__":
    agent = Agent()
    agent.run()

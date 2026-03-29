"""Точка входа для ИИ агента."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import Agent


def main():
    """Запуск ИИ агента."""
    agent = Agent()
    agent.run()


if __name__ == "__main__":
    main()

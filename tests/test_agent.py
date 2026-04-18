"""Тесты для ИИ агента."""

import pytest
from src.agent import Agent


class TestAgent:
    """Тесты для класса Agent."""

    def test_agent_initialization(self):
        """Проверка корректной инициализации агента."""
        agent = Agent()
        assert agent is not None

    def test_agent_name_default(self):
        """Проверка имени агента по умолчанию."""
        agent = Agent()
        assert isinstance(agent.name, str)

    def test_agent_run(self):
        """Проверка метода запуска агента."""
        agent = Agent()
        # Не должно вызывать исключений
        agent.run()


if __name__ == "__main__":
    pytest.main([__file__])

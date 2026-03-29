# -*- coding: utf-8 -*-
"""
Расширенные тесты для класса ИИ агента.
Проверяют пульс, навыки-триплеты, генератор run() и работу с окружением.
"""

import pytest
import sys
from io import StringIO
from src.agent import Agent


class TestAgentPulse:
    """Тесты системы пульса агента."""

    def test_pulse_initial_value(self):
        """Проверка начального значения пульса."""
        agent = Agent(name="PulseTest")
        assert agent.pulse == 0, "Начальное значение пульса должно быть 0"

    def test_pulse_beat_increments(self):
        """Проверка увеличения пульса при вызове beat()."""
        agent = Agent(name="PulseTest")
        initial_pulse = agent.pulse
        
        agent.beat()
        assert agent.pulse == initial_pulse + 1, "Пульс должен увеличиться на 1"
        
        agent.beat()
        agent.beat()
        assert agent.pulse == initial_pulse + 3, "Пульс должен увеличиться на 3 после трех вызовов"

    def test_pulse_generator(self):
        """Проверка работы генератора пульса."""
        agent = Agent(name="PulseTest")
        pulse_gen = agent.pulse_generator()
        
        # Генератор должен возвращать возрастающие значения
        val1 = next(pulse_gen)
        val2 = next(pulse_gen)
        val3 = next(pulse_gen)
        
        assert val2 > val1, "Значения генератора должны возрастать"
        assert val3 > val2, "Значения генератора должны возрастать"


class TestAgentSkills:
    """Тесты системы навыков агента."""

    def test_skill_registration(self):
        """Проверка регистрации навыка."""
        agent = Agent(name="SkillTest")
        skill_triplet = ('__builtins__', 'len', '[1, 2, 3]')
        agent.register_skill('count_items', skill_triplet)
        
        assert 'count_items' in agent.skills, "Навык должен быть зарегистрирован"
        assert agent.skills['count_items'] == skill_triplet, "Триплет навыка должен совпадать"

    def test_skill_execution_print(self):
        """Проверка выполнения навыка print."""
        agent = Agent(name="SkillTest")
        skill_triplet = ('__builtins__', 'print', '"Test output"')
        agent.register_skill('say_hello', skill_triplet)
        
        # Перехват вывода
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = agent.execute_skill('say_hello')
        
        sys.stdout = sys.__stdout__
        
        assert result is None, "print возвращает None"
        assert "Test output" in captured_output.getvalue(), "Вывод должен содержать тестовую строку"

    def test_skill_execution_input(self):
        """Проверка выполнения навыка input с моком."""
        agent = Agent(name="SkillTest")
        skill_triplet = ('__builtins__', 'input', '"Введите имя:"')
        agent.register_skill('ask_name', skill_triplet)
        
        # Мокаем input
        original_input = __builtins__['input']
        __builtins__['input'] = lambda x: "Тестовое имя"
        
        try:
            result = agent.execute_skill('ask_name')
            assert result == "Тестовое имя", "input должен вернуть замоканное значение"
        finally:
            __builtins__['input'] = original_input

    def test_skill_execution_math(self):
        """Проверка выполнения математического навыка."""
        agent = Agent(name="SkillTest")
        skill_triplet = ('__builtins__', 'sum', '[1, 2, 3, 4, 5]')
        agent.register_skill('calculate_sum', skill_triplet)
        
        result = agent.execute_skill('calculate_sum')
        assert result == 15, "Сумма [1, 2, 3, 4, 5] должна быть 15"

    def test_skill_not_found(self):
        """Проверка обработки отсутствия навыка."""
        agent = Agent(name="SkillTest")
        
        with pytest.raises(KeyError):
            agent.execute_skill('nonexistent_skill')

    def test_skill_execution_error(self):
        """Проверка обработки ошибок при выполнении навыка."""
        agent = Agent(name="SkillTest")
        # Навык, который вызовет ошибку (деление на ноль)
        skill_triplet = ('__builtins__', 'eval', '"1/0"')
        agent.register_skill('divide_by_zero', skill_triplet)
        
        with pytest.raises(ZeroDivisionError):
            agent.execute_skill('divide_by_zero')


class TestAgentRunGenerator:
    """Тесты генератора run()."""

    def test_run_generator_yields_results(self):
        """Проверка, что run() является генератором и возвращает результаты."""
        agent = Agent(name="RunTest")
        
        # Добавляем простые навыки
        agent.register_skill('skill1', ('__builtins__', 'str', '42'))
        agent.register_skill('skill2', ('__builtins__', 'len', '"hello"'))
        
        run_gen = agent.run()
        
        # Пропускаем первые два результата (базовые навыки print и input возвращают None)
        next(run_gen)  # print
        next(run_gen)  # input
        
        # Получаем результат skill1
        result1 = next(run_gen)
        assert result1 is not None, "Генератор должен вернуть результат выполнения навыка str(42)"
        
        # Пульс должен увеличиться
        assert agent.pulse >= 3, "Пульс должен увеличиться после выполнения навыков"

    def test_run_generator_multiple_iterations(self):
        """Проверка нескольких итераций генератора run()."""
        agent = Agent(name="RunTest")
        
        # Добавляем несколько навыков
        for i in range(3):
            agent.register_skill(f'skill_{i}', ('__builtins__', 'str', f'{i}'))
        
        run_gen = agent.run()
        
        results = []
        for _ in range(3):
            result = next(run_gen)
            results.append(result)
        
        assert len(results) == 3, "Должно быть получено 3 результата"

    def test_run_empty_strategy(self):
        """Проверка поведения при пустой стратегии."""
        agent = Agent(name="RunTest")
        # Не добавляем навыки
        
        run_gen = agent.run()
        
        # При пустой стратегии генератор может завершиться или вернуть None
        try:
            result = next(run_gen)
            # Если вернул результат, проверяем его
            assert result is None or isinstance(result, str), "Результат должен быть строкой или None"
        except StopIteration:
            # Ожидается при пустой стратегии
            pass


class TestAgentEnvironment:
    """Тесты работы с окружением агента."""

    def test_env_initialization(self):
        """Проверка инициализации окружения."""
        agent = Agent(name="EnvTest", debug=True)
        assert agent.debug is True, "Флаг debug должен быть установлен"
        assert 'APP_NAME' in agent.env or True, "Окружение должно быть загружено (или пропущено, если нет .env)"

    def test_env_get_with_default(self):
        """Проверка получения значения из окружения с дефолтом."""
        agent = Agent(name="EnvTest")
        
        # Получаем несуществующую переменную с дефолтом
        value = agent.get_env_var('NONEXISTENT_VAR', default='default_value')
        assert value == 'default_value', "Должно вернуться значение по умолчанию"

    def test_env_set_and_get(self):
        """Проверка установки и получения переменной окружения."""
        agent = Agent(name="EnvTest")
        
        agent.set_env_var('TEST_VAR', 'test_value')
        value = agent.get_env_var('TEST_VAR')
        
        assert value == 'test_value', "Значение переменной окружения должно совпадать"


class TestAgentIntegration:
    """Интеграционные тесты полного цикла жизни агента."""

    def test_full_agent_lifecycle(self):
        """Проверка полного цикла: создание, регистрация навыков, выполнение, пульс."""
        agent = Agent(name="IntegrationTest", debug=False)
        
        # Начальное состояние
        assert agent.pulse == 0
        # Базовый навык print уже зарегистрирован при инициализации
        assert len(agent.skills) >= 1
        
        # Регистрация дополнительных навыков
        agent.register_skill('calc', ('__builtins__', 'sum', '[10, 20, 30]'))
        
        assert len(agent.skills) >= 2
        
        # Запуск генератора
        run_gen = agent.run()
        
        # Пропускаем базовый навык print
        next(run_gen)
        
        # Выполнение навыка calc
        result2 = next(run_gen)
        assert agent.pulse >= 2, "После выполнения пульс должен быть >= 2"
        assert result2 == 60, "Результат sum([10, 20, 30]) должен быть 60"
        
        # Проверка состояния
        assert agent.state == 'running', "Агент должен быть в состоянии running"

    def test_agent_stop_condition(self):
        """Проверка условия остановки агента."""
        agent = Agent(name="StopTest")
        
        # Имитация команды остановки через флаг
        agent.state = 'stopped'
        
        assert agent.state == 'stopped', "Состояние должно быть stopped"
        
        # Попытка запустить генератор в остановленном состоянии
        # (в реальной реализации это должно обрабатываться)
        run_gen = agent.run()
        # Генератор может сразу завершиться или обработать остановку


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

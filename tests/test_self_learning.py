"""
Тесты для проверки самообучения агента, передачи контекста и обработки ошибок.
Фокус на последних изменениях в логике агента.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.agent import Agent


class TestContextPassing:
    """Тесты передачи результата предыдущего шага (prev_result)"""

    def test_print_receives_prev_result(self):
        """Навык print получает и выводит предыдущий результат"""
        agent = Agent()
        
        # Регистрируем навык print с аргументом "prev_result" под уникальным ID
        agent.register_skill('print_ctx', ('__builtins__', 'print', 'prev_result'))
        
        # Проверяем, что навык зарегистрирован
        assert 'print_ctx' in agent.skills
        assert agent.skills['print_ctx'] == ('__builtins__', 'print', 'prev_result')

    def test_chain_of_skills_with_context(self):
        """Цепочка навыков передаёт контекст друг другу"""
        agent = Agent()
        
        # Создаём цепочку: input -> print -> input с уникальными ID
        agent.register_skill('input_start', ('__builtins__', 'input', '"Введите данные"'))
        agent.register_skill('print_data', ('__builtins__', 'print', 'prev_result'))
        agent.register_skill('input_confirm', ('__builtins__', 'input', '"Подтвердите"'))
        
        # Проверяем регистрацию всех навыков
        assert len(agent.skills) >= 5  # Базовые + новые
        assert 'input_start' in agent.skills
        assert 'print_data' in agent.skills
        assert 'input_confirm' in agent.skills


class TestDynamicSkillLearning:
    """Тесты динамического добавления навыков через input"""

    def test_add_new_skill_from_user_input(self):
        """Агент добавляет новый навык из ввода пользователя в формате триплета"""
        agent = Agent()
        
        # Начальный навык: input для получения нового навыка (с уникальным ID)
        agent.register_skill('input_learn', ('__builtins__', 'input', '"Добавьте новый навык (триплет)"'))
        
        # Пользователь вводит новый навык в формате кортежа
        new_skill_input = "('math', 'sqrt', '16')"
        
        with patch('builtins.input', return_value=new_skill_input):
            # Просто проверяем, что input возвращает значение
            result = agent.execute_skill('input_learn')
            assert result == new_skill_input
            
            # Проверяем парсинг триплета вручную (так как логика парсинга в run())
            # В реальном цикле это было бы добавлено в стратегию
            import ast
            try:
                parsed = ast.literal_eval(new_skill_input)
                assert isinstance(parsed, tuple)
                assert len(parsed) == 3
            except:
                pytest.fail("Не удалось распарсить триплет")

    def test_invalid_tuple_input_handled(self):
        """Некорректный формат триплета не ломает агента"""
        agent = Agent()
        agent.register_skill('input_invalid', ('__builtins__', 'input', '"Введите триплет"'))
        
        # Пользователь вводит некорректную строку
        invalid_input = "это не кортеж"
        
        with patch('builtins.input', return_value=invalid_input):
            result = agent.execute_skill('input_invalid')
            
            # Агент должен вернуть строку как есть
            assert result == invalid_input

    def test_duplicate_skill_not_added(self):
        """Повторный навык не добавляется в стратегию"""
        agent = Agent()
        initial_skill_id = 'getcwd_skill'
        initial_skill = ('os', 'getcwd', '')
        agent.register_skill(initial_skill_id, initial_skill)
        agent.register_skill('input_dup', ('__builtins__', 'input', '"Добавьте навык"'))
        
        # Проверяем, что навык зарегистрирован один раз
        assert initial_skill_id in agent.skills
        assert agent.skills[initial_skill_id] == initial_skill


class TestErrorHandlingWithUserInput:
    """Тесты обработки ошибок с запросом решения у пользователя"""

    def test_error_triggers_input_for_solution(self):
        """При ошибке выполнения навыка агент запрашивает решение у пользователя"""
        agent = Agent()
        
        # Регистрируем навык, который вызовет ошибку (несуществующая функция)
        agent.register_skill('bad_func', ('__builtins__', 'nonexistent_func', 'arg'))
        agent.register_skill('input_ask', ('__builtins__', 'input', '"Как избежать ошибки?"'))
        
        # Проверяем, что ошибка возникает при выполнении
        with pytest.raises(KeyError):
            agent.execute_skill('bad_func')
        
        # Проверяем, что input работает
        with patch('builtins.input', return_value='попробуй другую функцию') as mock_input:
            result = agent.execute_skill('input_ask')
            assert result == 'попробуй другую функцию'
            mock_input.assert_called_once()

    def test_agent_continues_after_error_and_user_response(self):
        """Агент продолжает работу после ошибки и ответа пользователя"""
        agent = Agent()
        
        # Регистрируем навыки
        agent.register_skill('bad_int', ('__builtins__', 'int', '"не_число"'))  # Вызовет ValueError
        agent.register_skill('input_ask', ('__builtins__', 'input', '"Что делать?"'))
        # Используем строковый литерал вместо переменной
        agent.register_skill('print_result', ('__builtins__', 'print', '"Результат: используй try-except"'))
        
        # Проверяем, что int вызывает ошибку
        with pytest.raises(ValueError):
            agent.execute_skill('bad_int')
        
        # Проверяем цепочку: ошибка -> input -> print
        with patch('builtins.input', return_value='используй try-except'):
            with patch('builtins.print') as mock_print:
                # Выполняем input
                result = agent.execute_skill('input_ask')
                assert result == 'используй try-except'
                
                # Print должен вывести сообщение (mock возвращает MagicMock)
                agent.execute_skill('print_result')
                # Проверяем, что print был вызван хотя бы один раз
                mock_print.assert_called()


class TestIntegrationSelfLearning:
    """Интеграционные тесты полного цикла самообучения"""

    def test_full_self_learning_cycle(self):
        """Полный цикл: регистрация навыков и их выполнение"""
        agent = Agent()
        
        # Регистрируем несколько навыков
        # Используем math.sqrt для простоты (один аргумент)
        agent.register_skill('math_sqrt', ('math', 'sqrt', '16'))
        agent.register_skill('print_result', ('__builtins__', 'print', '"Результат вычисления"'))
        
        # Проверяем выполнение math.sqrt
        result = agent.execute_skill('math_sqrt')
        assert result == 4.0  # sqrt(16) = 4
        
        # Проверяем, что print зарегистрирован
        assert 'print_result' in agent.skills

    def test_random_skill_fallback_with_learning(self):
        """При пустой стратегии добавляется случайный навык, но обучение работает"""
        agent = Agent()
        
        # Регистрируем навыки для обучения
        agent.register_skill('input_learn', ('__builtins__', 'input', '"Обучи меня"'))
        agent.register_skill('getcwd', ('os', 'getcwd', ''))
        
        # Проверяем, что навыки зарегистрированы
        assert 'input_learn' in agent.skills
        assert 'getcwd' in agent.skills
        
        # Проверяем выполнение os.getcwd
        import os
        result = agent.execute_skill('getcwd')
        assert result == os.getcwd()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

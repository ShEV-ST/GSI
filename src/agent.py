"""Основной модуль ИИ агента."""

from dotenv import load_dotenv
import os

load_dotenv()


import random

class Agent:
    """Базовый класс ИИ агента."""

    def __init__(self, name=None, debug=None):
        """Инициализация агента.
        
        Args:
            name (str, optional): Имя агента. По умолчанию из окружения или "ai_agent"
            debug (bool, optional): Режим отладки. По умолчанию из окружения
        """
        self.name = name if name is not None else os.getenv("AGENT_NAME", "ai_agent")
        if debug is not None:
            self.debug = debug
        else:
            self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.pulse_count = 0
        self.pulse = 0  # Свойство для доступа к текущему значению пульса
        self._pulse_gen = self.pulse_generator()
        self.skills = {}
        self.state = 'running'
        self.env = {}
        
        # Загрузка переменных окружения
        self._load_env()
        
        # Регистрация базовых навыков
        # Навык print: выводит приветственное сообщение
        self.register_skill('print', ('__builtins__', 'print', '"Привет от агента!"'))
        
        # Навык input: запрашивает команду у пользователя (необходим для команды "СТОП")
        self.register_skill('input', ('__builtins__', 'input', '"Введите команду (или СТОП для выхода): "'))

    def pulse_generator(self):
        """Генератор пульса агента.
        
        Увеличивает счетчик пульса при каждом вызове.
        Yield:
            int: Текущее значение счетчика пульса
        """
        while True:
            self.pulse_count += 1
            self.pulse = self.pulse_count  # Обновляем свойство pulse
            yield self.pulse_count
    
    def beat(self):
        """Сердцебиение агента.
        
        Вызывает генератор пульса для увеличения счетчика.
        
        Returns:
            int: Текущий номер пульса
        """
        return next(self._pulse_gen)

    def _load_env(self):
        """Загрузка переменных окружения в словарь агента."""
        self.env['APP_NAME'] = os.getenv("APP_NAME", "AI Agent App")
        self.env['DEBUG'] = str(self.debug)

    def get_env_var(self, key, default=None):
        """Получение переменной окружения.
        
        Args:
            key (str): Ключ переменной
            default: Значение по умолчанию
            
        Returns:
            Значение переменной или default
        """
        return self.env.get(key, default)

    def set_env_var(self, key, value):
        """Установка переменной окружения.
        
        Args:
            key (str): Ключ переменной
            value: Значение переменной
        """
        self.env[key] = value

    def register_skill(self, skill_id, triplet):
        """Регистрация навыка в виде триплета.
        
        Args:
            skill_id (str): Идентификатор навыка
            triplet (tuple): Кортеж (module, func_name, args_str)
        """
        self.skills[skill_id] = triplet
        if self.debug:
            print(f"Навык зарегистрирован: {skill_id}")

    def execute_skill(self, skill_id):
        """Выполнение навыка по идентификатору.
        
        Args:
            skill_id (str): Идентификатор навыка
            
        Returns:
            Результат выполнения функции или None
        """
        if skill_id not in self.skills:
            raise KeyError(f"Навык {skill_id} не найден")
        
        tr_inp = self.skills[skill_id]
        module_name, func_name, args_str = tr_inp
        
        # Получаем функцию из встроенной области видимости или импортируем модуль
        if module_name == '__builtins__':
            if isinstance(__builtins__, dict):
                func = __builtins__[func_name]
            else:
                func = getattr(__builtins__, func_name)
        else:
            import importlib
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
        
        # Выполняем функцию с аргументами
        result = func(eval(args_str)) if args_str else func()
        
        if self.debug:
            print(f"Выполнен навык {skill_id}, результат: {result}")
        return result

    def run(self):
        """Генератор основного цикла агента.
        
        Извлекает очередной навык из стратегии, выполняет его,
        делает один beat() и возвращает результат.
        Если стратегия пуста, добавляет случайный навык.
        
        Yield:
            Результат выполнения навыка или None
        
        Raises:
            StopIteration: При команде "СТОП"
        """
        print(f"[{self.name}] Запуск... (Режим бесконечного исследования)")
        if self.debug:
            print("Режим отладки включён")
        
        # Стратегия - список навыков для выполнения
        strategy = list(self.skills.keys())
        
        while self.state == 'running':
            try:
                # Если стратегия пуста, добавляем случайный навык
                if not strategy:
                    if self.skills:
                        random_skill_name = random.choice(list(self.skills.keys()))
                        # Для input используем подсказку, для print - сообщение
                        if random_skill_name == 'input':
                            # Обновляем аргумент в триплете для следующего вызова
                            old_triplet = self.skills[random_skill_name]
                            new_triplet = (old_triplet[0], old_triplet[1], "'Введите команду (или СТОП): '")
                            self.skills[random_skill_name] = new_triplet
                        
                        strategy.append(random_skill_name)
                        print(f"[{self.name}] Стратегия пуста. Добавлен случайный навык: {random_skill_name}")
                    else:
                        print(f"[{self.name}] Нет доступных навыков. Остановка.")
                        self.state = 'stopped'
                        continue

                skill_id = strategy.pop(0)
                
                # Выполнение навыка
                result = self.execute_skill(skill_id)
                
                # Проверка результата навыка input на команду "СТОП"
                if skill_id == 'input' and isinstance(result, str):
                    if result.strip().upper() == 'СТОП':
                        print(f"\n[{self.name}] Получена команда остановки. Завершение работы.")
                        self.state = 'stopped'
                        yield f"Остановлено пользователем: {result}"
                        break
                
                # Удар пульса
                self.beat()
                
                # Возврат результата генератором
                yield result
                
            except Exception as e:
                error_msg = f"Ошибка в цикле: {e}"
                print(f"[{self.name}] {error_msg}")
                self.beat()
                yield f"Error: {error_msg}"
        
        print(f"\n[{self.name}] Агент завершил работу.")


if __name__ == "__main__":
    agent = Agent()
    agent.run()

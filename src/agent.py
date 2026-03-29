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
        self.pulse_count = 0
        self._pulse_gen = self.pulse_generator()
        self.skills = {}
        
        # Регистрация базовых навыков
        self.register_skill('__builtins__', 'print', '"Привет от агента!"')
        # Навык input закомментирован для автоматического запуска, так как требует ввода пользователя
        # self.register_skill('__builtins__', 'input', '"Введите данные: "')

    def pulse_generator(self):
        """Генератор пульса агента.
        
        Увеличивает счетчик пульса при каждом вызове.
        Yield:
            int: Текущее значение счетчика пульса
        """
        while True:
            self.pulse_count += 1
            yield self.pulse_count
    
    def beat(self):
        """Сердцебиение агента.
        
        Вызывает генератор пульса для увеличения счетчика.
        
        Returns:
            int: Текущий номер пульса
        """
        return next(self._pulse_gen)

    def register_skill(self, module, func_name, args_str):
        """Регистрация навыка в виде триплета.
        
        Args:
            module (str): Имя модуля (например, '__builtins__')
            func_name (str): Имя функции
            args_str (str): Строка аргументов для передачи
        """
        skill_id = f"{module}.{func_name}"
        self.skills[skill_id] = (module, func_name, args_str)
        if self.debug:
            print(f"Навык зарегистрирован: {skill_id}")

    def execute_skill(self, skill_id):
        """Выполнение навыка по идентификатору.
        
        Args:
            skill_id (str): Идентификатор навыка (module.func_name)
            
        Returns:
            Результат выполнения функции или None
        """
        if skill_id not in self.skills:
            print(f"Ошибка: навык {skill_id} не найден")
            return None
        
        tr_inp = self.skills[skill_id]
        try:
            # Выполнение триплета: module.function(args)
            result = eval(f"{tr_inp[0]}.{tr_inp[1]}({tr_inp[2]})")
            if self.debug:
                print(f"Выполнен навык {skill_id}, результат: {result}")
            return result
        except Exception as e:
            print(f"Ошибка выполнения навыка {skill_id}: {e}")
            return None

    def run(self):
        """Запуск основного цикла агента."""
        print(f"Запуск {self.name}...")
        if self.debug:
            print("Режим отладки включён")
        
        # Демонстрация пульса
        print("\n--- Демонстрация пульса ---")
        for i in range(5):
            pulse = self.beat()
            print(f"Пульс #{pulse}: тук-тук!")
        
        # Демонстрация навыков
        print("\n--- Демонстрация навыков ---")
        for skill_id in self.skills:
            print(f"Выполняем навык: {skill_id}")
            self.execute_skill(skill_id)
        
        print("\nАгент готов к работе.")


if __name__ == "__main__":
    agent = Agent()
    agent.run()

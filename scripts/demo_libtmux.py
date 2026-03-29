#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация возможностей библиотеки libtmux.

Этот скрипт показывает, как программно управлять сессиями tmux:
1. Создание новой сессии.
2. Разбиение окон на панели.
3. Запуск команд в конкретных панелях.
4. Чтение вывода из панелей.
5. Корректное завершение работы.
"""

import time
import sys
from libtmux import Server, exc


def main():
    print("=== Демонстрация работы с libtmux ===\n")

    # Подключаемся к серверу tmux (должен быть запущен)
    server = Server()

    session_name = "demo_agent_session"

    # 1. Проверка и очистка: если сессия уже есть, убиваем её для чистоты эксперимента
    existing_session = server.get_by_id(f"${session_name}")
    if existing_session:
        print(f"⚠️  Сессия '{session_name}' уже существует. Убиваем её...")
        existing_session.kill_session()
        time.sleep(0.5)

    try:
        # 2. Создание новой сессии
        print(f"🚀 Создаем новую сессию: {session_name}...")
        session = server.new_session(
            session_name=session_name,
            kill_session=True,  # Убить если есть (дублирующая страховка)
            attach=False        # Не переключать текущий терминал на эту сессию
        )
        print(f"✅ Сессия создана. ID: {session.id}")

        # Получаем первое окно и панель по умолчанию
        window = session.attached_window
        window.rename_window("main_dashboard")
        pane_main = window.attached_pane

        # Настройка главной панели
        pane_main.send_keys("echo '=== Панель управления агентом ==='")
        pane_main.send_keys("echo 'Статус: Ожидание...'")
        time.sleep(0.5)

        # 3. Разбиение окна на панели
        print("\n🔪 Разбиваем окно на панели...")
        
        # Разбиваем горизонтально (снизу появляется новая панель)
        pane_bottom = window.split_window(attach=False)
        pane_bottom.send_keys("echo '>>> Панель логов запущена'")
        
        # Разбиваем верхнюю панель вертикально (справа появляется новая)
        pane_right = pane_main.split_window(attach=False, vertical=False) # vertical=False значит сплит по вертикали (колонки)
        # Примечание: в tmux split-window -v делает горизонтальное разделение (панели друг под другом), 
        # а -h делает вертикальное (панели рядом). 
        # В libtmux split_window(vertical=True) -> -v (горизонтальный сплит, панели сверху/снизу)
        # В libtmux split_window(vertical=False) -> -h (вертикальный сплит, панели слева/справа)
        
        pane_right.send_keys("echo '>>> Панель мониторинга ресурсов'")
        pane_right.send_keys("python3 -c \"import psutil; print(f'CPU: {psutil.cpu_percent()}%')\"")

        # Переназовем панели для наглядности (через заголовки окон, так как у панелей нет имен, но мы можем менять их заголовки через команды)
        # Для простоты просто выведем информацию в них.
        
        time.sleep(1)

        # 4. Чтение вывода из панелей
        print("\n📖 Читаем вывод из панелей...")
        
        def read_pane(pane_obj, name):
            """Читает последние строки из панели."""
            try:
                # capture_pane возвращает список строк
                output = pane_obj.capture_pane()
                text = "\n".join(output).strip()
                if text:
                    print(f"[{name}]:\n{text}")
                else:
                    print(f"[{name}]: (пусто)")
            except Exception as e:
                print(f"[{name}]: Ошибка чтения: {e}")

        read_pane(pane_main, "Главная панель")
        read_pane(pane_right, "Мониторинг")
        read_pane(pane_bottom, "Логи")

        # 5. Отправка длительной команды в фон
        print("\n⏳ Запускаем долгий процесс в фоновой панели...")
        pane_bottom.send_keys("echo 'Запуск таймера на 10 секунд...'")
        pane_bottom.send_keys('for i in $(seq 1 5); do echo "Тик $i"; sleep 1; done; echo "Готово!"')
        
        # Ждем немного, чтобы процесс начался
        time.sleep(2)
        
        print("\n🔄 Обновленный статус панелей:")
        read_pane(pane_bottom, "Логи (обновлено)")

        # 6. Список всех окон в сессии
        print(f"\n📋 Список окон в сессии '{session_name}':")
        for w in session.windows:
            print(f" - Окно #{w.index}: {w.name} (ID: {w.id})")
            for p in w.panes:
                print(f"    └─ Панель ID: {p.id}")

        print("\n💡 Сессия активна! Вы можете подключиться к ней вручную:")
        print(f"   tmux attach -t {session_name}")
        print("\n⏸️  Пауза 5 секунд перед очисткой...")
        time.sleep(5)

    except exc.LibTmuxException as e:
        print(f"❌ Ошибка libtmux: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        # 7. Очистка: убиваем демонстрационную сессию
        print("\n🧹 Очистка: удаляем тестовую сессию...")
        try:
            if 'session' in locals():
                session.kill_session()
                print("✅ Сессия удалена.")
        except Exception:
            pass

    print("\n=== Демонстрация завершена ===")


if __name__ == "__main__":
    # Проверка наличия tmux
    import shutil
    if not shutil.which("tmux"):
        print("❌ Ошибка: утилита 'tmux' не найдена в PATH.")
        print("Установите её (apt install tmux / brew install tmux) и попробуйте снова.")
        sys.exit(1)
    
    # Проверка, запущен ли сервер tmux
    # Если мы внутри tmux, сервер точно запущен. Если нет - libtmux может не подключиться к несуществующему серверу.
    # Но libtmux может попробовать поднять новый сервер, если настроен.
    # В данном контексте (OpenHands) мы обычно внутри tmux.
    
    main()

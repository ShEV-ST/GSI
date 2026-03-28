#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор пользователей, процессов и сессий.
Демонстрирует возможности psutil для работы с пользователями и процессами.
"""

import psutil
from datetime import datetime


def get_active_users():
    """Получить список активных пользователей."""
    print("=" * 60)
    print("АКТИВНЫЕ ПОЛЬЗОВАТЕЛИ")
    print("=" * 60)
    
    users = psutil.users()
    
    if not users:
        print("Нет активных пользователей.")
        return []
    
    for i, user in enumerate(users, 1):
        print(f"\nПользователь #{i}:")
        print(f"  Имя: {user.name}")
        print(f"  Терминал: {user.terminal}")
        print(f"  Хост: {user.host}")
        print(f"  Время входа: {datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Время сессии: {(datetime.now() - datetime.fromtimestamp(user.started))}")
    
    return users


def get_process_tree(parent=None, indent=0, max_depth=3):
    """Рекурсивно получить дерево процессов."""
    if indent > max_depth:
        return
    
    try:
        if parent is None:
            # Получаем все корневые процессы (без родителей или с PID 0/1)
            processes = []
            for p in psutil.process_iter():
                try:
                    pinfo = p.as_dict(attrs=['pid', 'ppid'])
                    if pinfo['ppid'] in (0, 1):
                        processes.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            processes = parent.children(recursive=False)
        
        for proc in sorted(processes, key=lambda p: p.pid):
            try:
                with proc.oneshot():
                    pid = proc.pid
                    name = proc.name()
                    status = proc.status()
                    
                    prefix = "  " * indent
                    if indent == 0:
                        print(f"{prefix}├─ PID: {pid}, Имя: {name}, Статус: {status}")
                    else:
                        print(f"{prefix}└─ PID: {pid}, Имя: {name}, Статус: {status}")
                    
                    # Рекурсивный вызов для потомков
                    get_process_tree(proc, indent + 1, max_depth)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        print(f"Ошибка при получении дерева процессов: {e}")


def analyze_process_details(proc):
    """Получить детальную информацию о процессе."""
    try:
        with proc.oneshot():
            info = {}
            info['pid'] = proc.pid
            info['name'] = proc.name()
            info['status'] = proc.status()
            info['username'] = proc.username()
            info['cpu_percent'] = proc.cpu_percent(interval=0.1)
            info['memory_percent'] = proc.memory_percent()
            info['memory_info'] = proc.memory_info()
            info['num_threads'] = proc.num_threads()
            info['num_fds'] = proc.num_fds() if hasattr(proc, 'num_fds') else 'N/A'
            info['create_time'] = datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')
            info['cmdline'] = ' '.join(proc.cmdline()) if proc.cmdline() else proc.name()
            
            return info
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def get_top_processes(n=5):
    """Получить топ процессов по использованию памяти."""
    print("\n" + "=" * 60)
    print(f"ТОП {n} ПРОЦЕССОВ ПО ИСПОЛЬЗОВАНИЮ ПАМЯТИ")
    print("=" * 60)
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Сортировка по использованию памяти
    top_processes = sorted(processes, key=lambda p: p.get('memory_percent', 0), reverse=True)[:n]
    
    for i, proc in enumerate(top_processes, 1):
        print(f"\n{i}. Процесс: {proc['name']}")
        print(f"   PID: {proc['pid']}")
        print(f"   Использование памяти: {proc['memory_percent']:.2f}%")
        
        # Получаем детальную информацию
        try:
            p = psutil.Process(proc['pid'])
            details = analyze_process_details(p)
            if details:
                print(f"   Пользователь: {details['username']}")
                print(f"   CPU: {details['cpu_percent']:.1f}%")
                print(f"   Потоков: {details['num_threads']}")
                print(f"   Статус: {details['status']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def get_summary_stats():
    """Получить сводную статистику."""
    print("\n" + "=" * 60)
    print("СВОДНАЯ СТАТИСТИКА")
    print("=" * 60)
    
    # Количество процессов
    process_count = len(psutil.pids())
    print(f"Всего процессов: {process_count}")
    
    # Количество пользователей
    users = psutil.users()
    print(f"Активных пользователей: {len(users)}")
    
    # Общее использование CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"Общая загрузка CPU: {cpu_percent}%")
    
    # Общее использование памяти
    memory = psutil.virtual_memory()
    print(f"Использование памяти: {memory.percent}%")
    
    # Загрузочное время системы
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Время загрузки системы: {boot_time}")


def main():
    """Основная функция."""
    print("Запуск анализатора пользователей, процессов и сессий...")
    print(f"Время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Активные пользователи
    get_active_users()
    
    # 2. Топ процессов по памяти
    get_top_processes(5)
    
    # 3. Дерево процессов (ограниченная глубина)
    print("\n" + "=" * 60)
    print("ДЕРЕВО ПРОЦЕССОВ (первые уровни)")
    print("=" * 60)
    get_process_tree(max_depth=2)
    
    # 4. Сводная статистика
    get_summary_stats()
    
    print("\n" + "=" * 60)
    print("Анализ завершен!")
    print("=" * 60)


if __name__ == "__main__":
    main()

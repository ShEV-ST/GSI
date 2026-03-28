#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация возможностей модуля psutil.
Скрипт отображает информацию о системе: процессор, память, диск, сеть и процессы.
"""

import psutil
import os
import platform
from datetime import datetime


def print_separator(title: str) -> None:
    """Вывод разделителя с заголовком."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def get_cpu_info() -> None:
    """Отображение информации о процессоре."""
    print_separator("ИНФОРМАЦИЯ О ПРОЦЕССОРЕ (CPU)")
    
    # Количество логических и физических ядер
    print(f"Логические ядра: {psutil.cpu_count(logical=True)}")
    print(f"Физические ядра: {psutil.cpu_count(logical=False)}")
    
    # Частота процессора
    freq = psutil.cpu_freq()
    if freq:
        print(f"Текущая частота: {freq.current:.2f} МГц")
        print(f"Максимальная частота: {freq.max:.2f} МГц")
        print(f"Минимальная частота: {freq.min:.2f} МГц")
    
    # Загрузка процессора
    print(f"\nЗагрузка процессора (1 сек): {psutil.cpu_percent(interval=1)}%")
    
    # Загрузка по ядрам
    print("\nЗагрузка по ядрам:")
    for i, percentage in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
        print(f"  Ядро {i}: {percentage}%")


def get_memory_info() -> None:
    """Отображение информации об оперативной памяти."""
    print_separator("ИНФОРМАЦИЯ ОБ ОПЕРАТИВНОЙ ПАМЯТИ (RAM)")
    
    mem = psutil.virtual_memory()
    
    print(f"Всего: {mem.total / (1024**3):.2f} ГБ")
    print(f"Доступно: {mem.available / (1024**3):.2f} ГБ")
    print(f"Используется: {mem.used / (1024**3):.2f} ГБ ({mem.percent}%)")
    print(f"Свободно: {mem.free / (1024**3):.2f} ГБ")
    
    # Swap память
    swap = psutil.swap_memory()
    print(f"\nSwap всего: {swap.total / (1024**3):.2f} ГБ")
    print(f"Swap используется: {swap.percent}%")


def get_disk_info() -> None:
    """Отображение информации о дисках."""
    print_separator("ИНФОРМАЦИЯ О ДИСКАХ")
    
    # Разделы диска
    print("Разделы диска:")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"\n  Устройство: {partition.device}")
            print(f"  Точка монтирования: {partition.mountpoint}")
            print(f"  Файловая система: {partition.fstype}")
            print(f"  Всего: {usage.total / (1024**3):.2f} ГБ")
            print(f"  Свободно: {usage.free / (1024**3):.2f} ГБ")
            print(f"  Используется: {usage.percent}%")
        except PermissionError:
            print(f"\n  Устройство: {partition.device} (нет доступа)")


def get_network_info() -> None:
    """Отображение информации о сети."""
    print_separator("ИНФОРМАЦИЯ О СЕТИ")
    
    # Статистика сетевых интерфейсов
    print("Статистика сетевых интерфейсов:")
    net_io = psutil.net_io_counters(pernic=True)
    for interface, stats in net_io.items():
        print(f"\n  Интерфейс: {interface}")
        print(f"    Отправлено байт: {stats.bytes_sent / (1024**2):.2f} МБ")
        print(f"    Получено байт: {stats.bytes_recv / (1024**3):.2f} МБ")
        print(f"    Пакетов отправлено: {stats.packets_sent}")
        print(f"    Пакетов получено: {stats.packets_recv}")


def get_process_info(limit: int = 5) -> None:
    """Отображение информации о процессах."""
    print_separator(f"ТОП-{limit} ПРОЦЕССОВ ПО ИСПОЛЬЗОВАНИЮ ПАМЯТИ")
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            pinfo = proc.info
            if pinfo['memory_percent'] is not None:
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Сортировка по использованию памяти
    processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    
    print(f"{'PID':<8} {'Имя процесса':<25} {'Память %':<10} {'CPU %':<10}")
    print("-" * 55)
    
    for proc in processes[:limit]:
        pid = proc['pid']
        name = proc['name'] or 'N/A'
        mem = f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else 'N/A'
        cpu = f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else 'N/A'
        print(f"{pid:<8} {name:<25} {mem:<10} {cpu:<10}")


def get_system_info() -> None:
    """Отображение общей информации о системе."""
    print_separator("ОБЩАЯ ИНФОРМАЦИЯ О СИСТЕМЕ")
    
    # Информация об ОС через платформу
    uname = platform.uname()
    print(f"ОС: {uname.system}")
    print(f"Версия ОС: {uname.version}")
    print(f"Архитектура: {uname.machine}")
    print(f"Имя хоста: {uname.node}")
    
    # Время загрузки системы
    boot_time = psutil.boot_time()
    boot_datetime = datetime.fromtimestamp(boot_time)
    print(f"Время загрузки системы: {boot_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Время работы системы
    uptime = datetime.now() - boot_datetime
    print(f"Время работы: {uptime}")


def main():
    """Основная функция демонстрации."""
    print("\n" + "*" * 60)
    print(" ДЕМОСТРАЦИЯ ВОЗМОЖНОСТЕЙ МОДУЛЯ PSUTIL")
    print("*" * 60)
    print(f"Дата запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Текущий процесс: {os.getpid()}")
    
    try:
        get_system_info()
        get_cpu_info()
        get_memory_info()
        get_disk_info()
        get_network_info()
        get_process_info()
        
        print("\n" + "=" * 60)
        print(" Демонстрация завершена успешно!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

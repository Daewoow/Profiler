import importlib
import logging
import time
import types

from collections import defaultdict
from utils import Utils

logging.basicConfig(level=logging.ERROR, format='Ошибка: %(asctime)s %(message)s')


class Profiler:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "call_count": 0,
            "total_time": 0,
            "cumulative_time": 0,
            "min_time": float('inf'),
            "max_time": float('-inf')
        })
        self.stack = []
        self.sorted_column = None

    def _profile_function(self, func, *args, **kwargs):
        """
        Засекает время начала и конца
        :param func: функция
        :param args: аргументы функции
        :param kwargs: аргументы функции по ключу
        :return: обёрнутая функция
        """
        function_name = f"{func.__name__} ({func.__code__.co_filename}:{func.__code__.co_firstlineno})"
        start_time = time.time()
        self.stack.append((function_name, start_time))

        try:
            result = func(*args, **kwargs)
        except TypeError:
            result = "0"
        finally:
            elapsed_time = time.time() - start_time
            self.stack.pop()

            stat = self.stats[function_name]
            stat["call_count"] += 1
            stat["total_time"] += elapsed_time
            stat["min_time"] = min(stat["min_time"], elapsed_time)
            stat["max_time"] = max(stat["max_time"], elapsed_time)

            for caller_function, caller_start_time in self.stack:
                caller_stat = self.stats[caller_function]
                caller_stat["cumulative_time"] += elapsed_time

        return result

    def wrap_functions(self, module, seen=None) -> None:
        """
        Рекурсивно оборачивает все функции в модуле
        :param module: модуль
        :param seen: уже просмотренные модули
        :return: None
        """
        if seen is None:
            seen = set()

        if module in seen:
            return

        seen.add(module)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if isinstance(attr, types.FunctionType) and hasattr(attr, "__code__"):
                wrapped = self._make_wrapper(attr)
                setattr(module, attr_name, wrapped)

            elif isinstance(attr, type):
                for method_name in dir(attr):
                    method = getattr(attr, method_name)
                    if isinstance(method, (types.FunctionType, types.MethodType)) and hasattr(method, "__code__"):
                        original_function = method.__func__ if isinstance(method, types.MethodType) else method
                        if "Profiler" not in original_function.__module__:
                            wrapped = self._make_wrapper(original_function)
                            setattr(attr, method_name, wrapped)

    def _make_wrapper(self, func):
        """
        Создаёт обёртку для профилирования функции
        :param func: функция
        :return:
        """

        def wrapper(*args, **kwargs):
            return self._profile_function(func, *args, **kwargs)

        return wrapper

    def patch_builtin_methods(self, obj):
        """
        Переопределяет методы встроенных структур данных (list, dict, set) для замера времени выполнения.
        :param obj: объект, методы которого нужно переопределить
        """
        if isinstance(obj, (list, dict, set)):
            for method_name in dir(obj):
                method = getattr(obj, method_name)
                if callable(method):
                    def wrapper(*args, **kwargs):
                        return self._profile_function(method, self, *args, **kwargs)

                    setattr(obj, method_name, wrapper.__get__(obj))

    def run(self, command, sort=None) -> None:
        """
        Запускает профилирование
        :param command: Название модуля и метода
        :param sort: флаг сортировки (необязателен)
        """
        if sort is not None:
            if sort >= 5:
                logging.error("всего 5 столбцов для сортировки")
                return
            self.sorted_column = sort

        try:
            module_name, func_name = command.split(".")
        except ValueError:
            logging.error("название метода должно быть в формате module_name.method_name")
            return
        except IndexError:
            logging.error("название метода должно быть в формате module_name.method_name")
            return

        module = importlib.import_module(module_name)

        self.wrap_functions(module)

        target_function = getattr(module, func_name)
        start_time = time.time()
        try:
            self.patch_builtin_methods(target_function)
            target_function()
        finally:
            total_time = time.time() - start_time
            print(f"Всего времени: {total_time:.6f} секунд")
            Utils.print_stats(self.stats.items(), self.sorted_column)

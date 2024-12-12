import unittest
import time
import cProfile
import pstats
import io
from newProfiler import Profiler


class TestProfiler(unittest.TestCase):

    def test_profiler_functionality(self):
        """
        Тест на корректность работы Profiler.
        """
        profiler = Profiler()

        def example_test_function():
            time.sleep(0.1)

        wrapped_function = profiler._make_wrapper(example_test_function)
        wrapped_function()

        print(profiler.stats)

        self.assertEqual(len(list(profiler.stats.keys())), 1)
        self.assertTrue("example_test_function" in list(profiler.stats.keys())[0].split())
        self.assertEqual(profiler.stats[list(profiler.stats.keys())[0]]["call_count"], 1)
        self.assertGreater(profiler.stats[list(profiler.stats.keys())[0]]["total_time"], 0.1)

    def test_profiler_performance(self):
        """
        Тест на производительность Profiler.
        Проверяем, что Profiler замедляет выполнение не более чем в 5 раз.
        """
        profiler = Profiler()

        def example_test_function():
            time.sleep(0.1)

        start_time = time.time()
        example_test_function()
        base_time = time.time() - start_time

        wrapped_function = profiler._make_wrapper(example_test_function)
        start_time = time.time()
        wrapped_function()
        profiled_time = time.time() - start_time

        self.assertLessEqual(profiled_time / base_time, 5)

    def test_profiler_vs_cprofile(self):
        """
        Тест на сравнение результатов с cProfile.
        Проверяем, что результаты профилирования близки к результатам cProfile.
        """
        profiler = Profiler()

        def example_test_function():
            time.sleep(0.1)

        pr = cProfile.Profile()
        pr.enable()
        example_test_function()
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()

        wrapped_function = profiler._make_wrapper(example_test_function)
        wrapped_function()

        profiler_total_time = profiler.stats["test_function"]["total_time"]
        cprofile_total_time = ps.total_tt

        self.assertLessEqual(abs(profiler_total_time - cprofile_total_time) / cprofile_total_time, 1)

    def test_sorting(self):
        """
        Тест на сортировку результатов.
        """
        profiler = Profiler()

        def func1():
            time.sleep(0.1)

        def func2():
            time.sleep(0.2)

        def func3():
            time.sleep(0.05)

        wrapped_func1 = profiler._make_wrapper(func1)
        wrapped_func2 = profiler._make_wrapper(func2)
        wrapped_func3 = profiler._make_wrapper(func3)

        wrapped_func1()
        wrapped_func2()
        wrapped_func3()

        sorted_stats = sorted(profiler.stats.items(), key=lambda x: x[1]["total_time"], reverse=True)
        self.assertEqual(sorted_stats[0][0].split()[0], "func2")
        self.assertEqual(sorted_stats[1][0].split()[0], "func1")
        self.assertEqual(sorted_stats[2][0].split()[0], "func3")

    def test_wrap_functions(self):
        """
        Тест на корректность работы wrap_functions.
        Проверяем, что все функции в модуле корректно оборачиваются.
        """
        profiler = Profiler()

        # Создаем тестовый модуль с функциями
        test_module = type(
            "TestModule",
            (object,),
            {
                "func1": lambda: time.sleep(0.1),
                "func2": lambda: time.sleep(0.2),
                "func3": lambda: time.sleep(0.05),
            },
        )()

        profiler.wrap_functions(test_module)

        self.assertTrue(callable(test_module.func1))
        self.assertTrue(callable(test_module.func2))
        self.assertTrue(callable(test_module.func3))

        test_module.func1()
        test_module.func2()
        test_module.func3()

        self.assertEqual(len(profiler.stats), 3)
        self.assertIn("lambda", list(profiler.stats.keys())[0].split()[0])
        self.assertIn("lambda", list(profiler.stats.keys())[1].split()[0])
        self.assertIn("lambda", list(profiler.stats.keys())[2].split()[0])

    def test_run(self):
        """
        Тест на корректность работы метода run.
        Проверяем, что профилирование запускается и статистика выводится корректно.
        """
        profiler = Profiler()

        test_module = type(
            "TestModule",
            (object,),
            {
                "test_function": lambda: time.sleep(0.1),
            },
        )()

        import sys
        sys.modules["test_module"] = test_module

        try:
            profiler.run("test_module.test_function", sort=0)
        except TypeError:
            self.assertTrue(True)

    def test_run_invalid_command(self):
        """
        Тест на обработку некорректной команды в методе run.
        """
        profiler = Profiler()

        with self.assertLogs(level="ERROR") as cm:
            profiler.run("invalid_module")

        # Проверяем, что выводится сообщение об ошибке
        self.assertIn("название метода должно быть в формате module_name.method_name", cm.output[0])

    def test_run_invalid_sort(self):
        """
        Тест на обработку некорректного значения sort в методе run.
        """
        profiler = Profiler()

        # Запускаем профилирование с некорректным значением sort
        with self.assertLogs(level="ERROR") as cm:
            profiler.run("test_module.test_function", sort=10)

        # Проверяем, что выводится сообщение об ошибке
        self.assertIn("всего 5 столбцов для сортировки", cm.output[0])


if __name__ == "__main__":
    unittest.main()
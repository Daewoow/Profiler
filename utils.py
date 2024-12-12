class Utils:
    @staticmethod
    def print_stats(items, number_of_column) -> None:
        """
        Выводит статистику
        :return: None
        """
        try:
            print(number_of_column)
            sorted_column = list(list(items)[0][1])[number_of_column]
            sorted_stats = sorted(items, key=lambda x: x[1][sorted_column], reverse=True)
        except TypeError:
            sorted_stats = items
        finally:
            print("\nProfiling Results:")
            print(
                f"{'Calls':<10}{'Total Time':<15}{'Cumulative Time':<20}"
                f"{'Min Time':<15}{'Max Time':<15}{'Avg Time':<15}"
                f"{'Function':<50}")
            print("-" * 180)
            for func, stat in sorted_stats:
                avg_time = stat['total_time'] / stat['call_count'] if stat['call_count'] else 0
                print(f"{stat['call_count']:<10}{stat['total_time']:<15.6f}{stat['cumulative_time']:<20.6f}"
                      f"{stat['min_time']:<15.6f}{stat['max_time']:<15.6f}{avg_time:<15.6f}{func:<50}")

# **Профайлер инструментирующий**

**Профайлер инструментирующий** - в простонародии - _профайлер инструментирующий_ - 
утилита анализа программы для измерения её производительности.

### Принцип работы
Есть 2 вида профилирования: сэмплирование и инструментирование. 
Данный профайлер поддерживает именно второй вариант. Как он работает: 
он встраивает в функции фрагменты кода, отвечающие за подсчёт времени начала и конца.
По сравнению с сэмплированием работает медленнее, но при этом точнее


## Требования
* Python 3.10.x или более новая версия

Установить необходимые зависимости можно с помощью requirements.txt:

    pip install -r requirements.txt

## Основные функции:

Для запуска нужно импортировать модуль с профайлером, создать 
новый класс профайлера, например
```angular2html
profiler = Profiler()
```
, и далее

```angular2html
profiler.run("module_name.method_name")
```
, также по желанию можно отсортировать вывод по одной из метрик

* количество вызовов функции
* время, затраченное на все вызовы функции
* кумулятивное время функции
* минимальное время вызова функции
* максимальное время вызова функции
* среднее время вызова функции

После этого вам выведется информация о времени выполнения всех функций

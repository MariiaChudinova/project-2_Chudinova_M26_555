"""Декораторы и замыкание для кэширования."""
import time

import prompt

from primitive_db.constants import CONFIRM_YES


def _copy_meta(wrapper, func):
    """Переносит имя и docstring исходной функции на обёртку."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_db_errors(func):
    """Перехватывает типовые ошибки БД и выводит понятное сообщение."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return _copy_meta(wrapper, func)


def confirm_action(action_name):
    """Фабрика декораторов: запрашивает подтверждение опасной операции."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != CONFIRM_YES:
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return _copy_meta(wrapper, func)

    return decorator


def log_time(func):
    """Замеряет и выводит время выполнения функции."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return _copy_meta(wrapper, func)


def create_cacher():
    """Возвращает функцию cache_result с кэшем в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает значение из кэша или вычисляет его через value_func."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
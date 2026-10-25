
import json

from primitive_db.constants import ID_COLUMN, TYPE_MAP, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

select_cache = create_cacher()


def _invalid_value(value):
    """Создаёт ошибку с сообщением о некорректном значении."""
    return ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


def _format_schema(schema):
    """Форматирует схему таблицы как 'ID:int, name:str'."""
    return ", ".join(f"{name}:{kind}" for name, kind in schema.items())


def _format_ids(records):
    """Возвращает ID записей через запятую."""
    return ", ".join(str(record[ID_COLUMN]) for record in records)


def _parse_columns(columns):
    """Проверяет столбцы вида 'имя:тип' и строит схему с ID в начале."""
    schema = {ID_COLUMN: "int"}
    for column in columns:
        name, separator, column_type = column.partition(":")
        if not separator or not name.isidentifier() or column_type not in VALID_TYPES:
            raise _invalid_value(column)
        if name == ID_COLUMN and column_type == "int":
            continue
        if name in schema:
            raise _invalid_value(column)
        schema[name] = column_type
    return schema


def _check_type(column_type, value):
    """Проверяет, что значение соответствует типу столбца."""
    if type(value) is not TYPE_MAP[column_type]:
        raise _invalid_value(value)


def _next_id(table_data):
    """Генерирует следующий ID: максимальный существующий + 1."""
    return max((record[ID_COLUMN] for record in table_data), default=0) + 1


def _matches(record, where_clause):
    """Проверяет, подходит ли запись под условие (значение и тип)."""
    return all(
        record[column] == value and type(record[column]) is type(value)
        for column, value in where_clause.items()
    )


def _filter_records(table_data, where_clause):
    """Возвращает записи, подходящие под условие (или все, если условия нет)."""
    if not where_clause:
        return list(table_data)
    return [record for record in table_data if _matches(record, where_clause)]


def require_table(metadata, table_name):
    """Проверяет существование таблицы; при отсутствии выводит ошибку."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


# 

@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт таблицу с автоматическим столбцом ID:int."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None
    if not table_name.isidentifier():
        raise _invalid_value(table_name)
    schema = _parse_columns(columns)
    metadata[table_name] = schema
    print(
        f'Таблица "{table_name}" успешно создана '
        f"со столбцами: {_format_schema(schema)}"
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if not require_table(metadata, table_name):
        return None
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return
    for table_name in metadata:
        print(f"- {table_name}")


@handle_db_errors
def table_info(metadata, table_name, table_data):
    """Выводит структуру таблицы и количество записей."""
    if not require_table(metadata, table_name):
        return
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {_format_schema(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")


#

@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    """Добавляет запись; ID генерируется автоматически."""
    if not require_table(metadata, table_name):
        return None
    schema = metadata[table_name]
    columns = [column for column in schema if column != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(
            f"Ожидалось значений: {len(columns)}, получено: {len(values)}."
        )
    record = {ID_COLUMN: _next_id(table_data)}
    for column, value in zip(columns, values):
        _check_type(schema[column], value)
        record[column] = value
    table_data.append(record)
    print(
        f'Запись с ID={record[ID_COLUMN]} успешно добавлена '
        f'в таблицу "{table_name}".'
    )
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи по условию; одинаковые запросы берутся из кэша."""
    key = json.dumps(
        {"data": table_data, "where": where_clause},
        ensure_ascii=False,
        sort_keys=True,
    )
    return select_cache(key, lambda: _filter_records(table_data, where_clause))


@handle_db_errors
def update(metadata, table_name, table_data, set_clause, where_clause):
    """Обновляет поля у записей, подходящих под условие."""
    if not require_table(metadata, table_name):
        return None
    schema = metadata[table_name]
    for column, value in set_clause.items():
        if column == ID_COLUMN:
            raise ValueError("Столбец ID изменять нельзя.")
        _check_type(schema[column], value)
    for column in where_clause:
        if column not in schema:
            raise KeyError(column)
    matched = _filter_records(table_data, where_clause)
    if not matched:
        print("Записи по условию не найдены.")
        return None
    for record in matched:
        record.update(set_clause)
    print(
        f'Записи с ID={_format_ids(matched)} в таблице "{table_name}" '
        "успешно обновлены."
    )
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_name, table_data, where_clause):
    """Удаляет записи, подходящие под условие."""
    matched = _filter_records(table_data, where_clause)
    if not matched:
        print("Записи по условию не найдены.")
        return None
    removed_ids = {record[ID_COLUMN] for record in matched}
    remaining = [r for r in table_data if r[ID_COLUMN] not in removed_ids]
    print(
        f'Записи с ID={_format_ids(matched)} успешно удалены '
        f'из таблицы "{table_name}".'
    )
    return remaining
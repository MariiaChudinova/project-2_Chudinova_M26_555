import shlex

import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import (
    DELETE_MAXSPLIT,
    DELETE_TOKENS,
    HELP_LINES,
    INSERT_MAXSPLIT,
    INSERT_TOKENS,
    KEYWORD_FROM,
    KEYWORD_INTO,
    KEYWORD_SET,
    KEYWORD_VALUES,
    KEYWORD_WHERE,
    META_FILE,
    MIN_CREATE_ARGS,
    PROMPT_TEXT,
    SELECT_ALL_TOKENS,
    SELECT_MAXSPLIT,
    SELECT_WHERE_TOKENS,
    TABLE_ARGS_COUNT,
    UPDATE_MAXSPLIT,
    UPDATE_TOKENS,
    USAGE_CREATE,
    USAGE_DELETE,
    USAGE_DROP,
    USAGE_INFO,
    USAGE_INSERT,
    USAGE_SELECT,
    USAGE_UPDATE,
)
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import (
    parse_assignments,
    parse_condition,
    parse_values,
    split_on_keyword,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справку по командам."""
    print("\n".join(HELP_LINES))


def print_records(schema, records):
    """Печатает записи таблицей prettytable."""
    if not records:
        print("Записи не найдены.")
        return
    table = PrettyTable()
    table.field_names = list(schema)
    for record in records:
        table.add_row([record[column] for column in schema])
    print(table)


def _usage_error(usage):
    """Создаёт ошибку с подсказкой по формату команды."""
    return ValueError(f"Неверный формат команды. Используйте: {usage}")


def _parse_where(text, usage):
    """Разбирает фрагмент 'where <столбец> = <значение>'."""
    parts = text.split(maxsplit=1)
    if len(parts) != TABLE_ARGS_COUNT or parts[0].lower() != KEYWORD_WHERE:
        raise _usage_error(usage)
    return parse_condition(parts[1])


@handle_db_errors
def handle_help(metadata, user_input):
    """Обрабатывает команду help."""
    print_help()


@handle_db_errors
def handle_list_tables(metadata, user_input):
    """Обрабатывает команду list_tables."""
    core.list_tables(metadata)


@handle_db_errors
def handle_create_table(metadata, user_input):
    """Обрабатывает команду create_table."""
    args = shlex.split(user_input)
    if len(args) < MIN_CREATE_ARGS:
        raise _usage_error(USAGE_CREATE)
    new_metadata = core.create_table(metadata, args[1], args[2:])
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)


@handle_db_errors
def handle_drop_table(metadata, user_input):
    """Обрабатывает команду drop_table."""
    args = shlex.split(user_input)
    if len(args) != TABLE_ARGS_COUNT:
        raise _usage_error(USAGE_DROP)
    table_name = args[1]
    if not core.require_table(metadata, table_name):
        return
    new_metadata = core.drop_table(metadata, table_name)
    if new_metadata is not None:
        save_metadata(META_FILE, new_metadata)
        delete_table_data(table_name)


@handle_db_errors
def handle_info(metadata, user_input):
    """Обрабатывает команду info."""
    args = shlex.split(user_input)
    if len(args) != TABLE_ARGS_COUNT:
        raise _usage_error(USAGE_INFO)
    table_name = args[1]
    if core.require_table(metadata, table_name):
        core.table_info(metadata, table_name, load_table_data(table_name))


@handle_db_errors
def handle_insert(metadata, user_input):
    """Обрабатывает команду insert into ... values (...)."""
    tokens = user_input.split(maxsplit=INSERT_MAXSPLIT)
    if (
        len(tokens) != INSERT_TOKENS
        or tokens[1].lower() != KEYWORD_INTO
        or tokens[3].lower() != KEYWORD_VALUES
    ):
        raise _usage_error(USAGE_INSERT)
    table_name = tokens[2]
    if not core.require_table(metadata, table_name):
        return
    values = parse_values(tokens[4])
    new_data = core.insert(metadata, table_name, load_table_data(table_name), values)
    if new_data is not None:
        save_table_data(table_name, new_data)


@handle_db_errors
def handle_select(metadata, user_input):
    """Обрабатывает команду select from ... [where ...]."""
    tokens = user_input.split(maxsplit=SELECT_MAXSPLIT)
    if len(tokens) < SELECT_ALL_TOKENS or tokens[1].lower() != KEYWORD_FROM:
        raise _usage_error(USAGE_SELECT)
    table_name = tokens[2]
    if not core.require_table(metadata, table_name):
        return
    where_clause = None
    if len(tokens) == SELECT_WHERE_TOKENS:
        where_clause = _parse_where(tokens[3], USAGE_SELECT)
    records = core.select(load_table_data(table_name), where_clause)
    if records is not None:
        print_records(metadata[table_name], records)


@handle_db_errors
def handle_update(metadata, user_input):
    """Обрабатывает команду update ... set ... where ..."""
    tokens = user_input.split(maxsplit=UPDATE_MAXSPLIT)
    if len(tokens) != UPDATE_TOKENS or tokens[2].lower() != KEYWORD_SET:
        raise _usage_error(USAGE_UPDATE)
    table_name = tokens[1]
    if not core.require_table(metadata, table_name):
        return
    set_text, where_text = split_on_keyword(tokens[3], KEYWORD_WHERE)
    set_clause = parse_assignments(set_text)
    where_clause = parse_condition(where_text)
    new_data = core.update(
        metadata, table_name, load_table_data(table_name), set_clause, where_clause
    )
    if new_data is not None:
        save_table_data(table_name, new_data)


@handle_db_errors
def handle_delete(metadata, user_input):
    """Обрабатывает команду delete from ... where ..."""
    tokens = user_input.split(maxsplit=DELETE_MAXSPLIT)
    if len(tokens) != DELETE_TOKENS or tokens[1].lower() != KEYWORD_FROM:
        raise _usage_error(USAGE_DELETE)
    table_name = tokens[2]
    if not core.require_table(metadata, table_name):
        return
    where_clause = _parse_where(tokens[3], USAGE_DELETE)
    new_data = core.delete(table_name, load_table_data(table_name), where_clause)
    if new_data is not None:
        save_table_data(table_name, new_data)


COMMAND_HANDLERS = {
    "create_table": handle_create_table,
    "drop_table": handle_drop_table,
    "list_tables": handle_list_tables,
    "insert": handle_insert,
    "select": handle_select,
    "update": handle_update,
    "delete": handle_delete,
    "info": handle_info,
    "help": handle_help,
}


def run():
    """Главный цикл: ввод команды, разбор, вызов обработчика."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(PROMPT_TEXT).strip()
        if not user_input:
            continue
        command = user_input.split(maxsplit=1)[0]
        if command.lower() == "exit":
            break
        handler = COMMAND_HANDLERS.get(command.lower())
        if handler is None:
            print(f"Функции {command} нет. Попробуйте снова.")
            continue
        handler(metadata, user_input)
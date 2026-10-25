"""Константы проекта."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
ENCODING = "utf-8"
JSON_INDENT = 4

ID_COLUMN = "ID"
VALID_TYPES = ("int", "str", "bool")
TYPE_MAP = {"int": int, "str": str, "bool": bool}
BOOL_LITERALS = {"true": True, "false": False}
QUOTES = ("'", '"')

PROMPT_TEXT = ">>>Введите команду: "
CONFIRM_YES = "y"

KEYWORD_INTO = "into"
KEYWORD_VALUES = "values"
KEYWORD_FROM = "from"
KEYWORD_SET = "set"
KEYWORD_WHERE = "where"

# Количество частей команд после разбиения по пробелам
TABLE_ARGS_COUNT = 2
MIN_CREATE_ARGS = 2
INSERT_MAXSPLIT = 4
INSERT_TOKENS = 5
SELECT_MAXSPLIT = 3
SELECT_ALL_TOKENS = 3
SELECT_WHERE_TOKENS = 4
UPDATE_MAXSPLIT = 3
UPDATE_TOKENS = 4
DELETE_MAXSPLIT = 3
DELETE_TOKENS = 4

USAGE_CREATE = "create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ..."
USAGE_DROP = "drop_table <имя_таблицы>"
USAGE_INFO = "info <имя_таблицы>"
USAGE_INSERT = "insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
USAGE_SELECT = "select from <имя_таблицы> [where <столбец> = <значение>]"
USAGE_UPDATE = (
    "update <имя_таблицы> set <столбец> = <значение> "
    "where <столбец> = <значение>"
)
USAGE_DELETE = "delete from <имя_таблицы> where <столбец> = <значение>"

HELP_LINES = (
    "\n***Операции с данными***",
    "Функции:",
    "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу",
    "<command> list_tables - показать список всех таблиц",
    "<command> drop_table <имя_таблицы> - удалить таблицу",
    "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
    " - создать запись.",
    "<command> select from <имя_таблицы> where <столбец> = <значение>"
    " - прочитать записи по условию.",
    "<command> select from <имя_таблицы> - прочитать все записи.",
    "<command> update <имя_таблицы> set <столбец1> = <новое_значение1>"
    " where <столбец_условия> = <значение_условия> - обновить запись.",
    "<command> delete from <имя_таблицы> where <столбец> = <значение>"
    " - удалить запись.",
    "<command> info <имя_таблицы> - вывести информацию о таблице.",
    "\nОбщие команды:",
    "<command> exit - выход из программы",
    "<command> help - справочная информация\n",
)
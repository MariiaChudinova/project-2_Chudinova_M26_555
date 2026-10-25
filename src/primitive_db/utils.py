
import json
import os

from primitive_db.constants import DATA_DIR, ENCODING, JSON_INDENT, META_FILE


def load_metadata(filepath=META_FILE):
    """Загружает метаданные из JSON-файла; если файла нет, возвращает {}."""
    try:
        with open(filepath, encoding=ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding=ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)


def _table_path(table_name):
    """Возвращает путь к файлу данных таблицы."""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загружает записи таблицы; если файла нет, возвращает пустой список."""
    try:
        with open(_table_path(table_name), encoding=ENCODING) as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет записи таблицы в data/<table_name>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_path(table_name), "w", encoding=ENCODING) as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)


def delete_table_data(table_name):
    """Удаляет файл данных таблицы, если он существует."""
    path = _table_path(table_name)
    if os.path.exists(path):
        os.remove(path)
"""Разбор значений, условий where/set и списка values."""
from primitive_db.constants import BOOL_LITERALS, QUOTES


def _invalid_value(token):
    """Создаёт ошибку с сообщением о некорректном значении."""
    return ValueError(f"Некорректное значение: {token}. Попробуйте снова.")


def parse_value(token):
    """Преобразует строку в str/bool/int; строки обязаны быть в кавычках."""
    token = token.strip()
    if len(token) >= 2 and token[0] in QUOTES and token[-1] == token[0]:
        return token[1:-1]
    if token.lower() in BOOL_LITERALS:
        return BOOL_LITERALS[token.lower()]
    try:
        return int(token)
    except ValueError:
        raise _invalid_value(token) from None


def split_outside_quotes(text, separator):
    """Делит строку по одиночному символу, игнорируя разделители в кавычках."""
    parts, current, quote = [], [], None
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in QUOTES:
            quote = char
            current.append(char)
        elif char == separator:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if quote:
        raise _invalid_value(text)
    parts.append("".join(current).strip())
    return parts


def split_on_keyword(text, keyword):
    """Делит строку на две части по ключевому слову вне кавычек."""
    quote = None
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = None
        elif char in QUOTES:
            quote = char
        elif char.isspace():
            start = index + 1
            end = start + len(keyword)
            if text[start:end].lower() == keyword and text[end:end + 1].isspace():
                return text[:index].strip(), text[end:].strip()
    raise ValueError(f"Ожидалось ключевое слово '{keyword}'.")


def parse_values(text):
    """Разбирает строку вида '("Sergei", 28, true)' в список значений."""
    text = text.strip()
    if len(text) < 2 or text[0] != "(" or text[-1] != ")":
        raise _invalid_value(text)
    return [parse_value(part) for part in split_outside_quotes(text[1:-1], ",")]


def parse_assignments(text):
    """Разбирает 'age = 28, name = "Ann"' в словарь {'age': 28, 'name': 'Ann'}."""
    result = {}
    for part in split_outside_quotes(text, ","):
        pieces = split_outside_quotes(part, "=")
        if len(pieces) != 2 or not pieces[0]:
            raise _invalid_value(part)
        result[pieces[0]] = parse_value(pieces[1])
    return result


def parse_condition(text):
    """Разбирает одно условие 'age = 28' в словарь {'age': 28}."""
    condition = parse_assignments(text)
    if len(condition) != 1:
        raise _invalid_value(text)
    return condition
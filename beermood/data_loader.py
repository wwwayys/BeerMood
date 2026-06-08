import json
from pathlib import Path

from models import Beer


def to_int(value, default=0):
    """Безопасно преобразовать значение в целое число.

    Принимает строки с запятой как десятичным разделителем.
    Используется для нормализации цены.

    Args:
        value: Преобразуемое значение.
        default: Возвращаемое значение при ошибке конвертации.

    Returns:
        Целое число или default, если преобразование невозможно.
    """

    try:
        # Заменяем запятую на точку и преобразуем значение в число
        return int(float(str(value).replace(",", ".")))
    except (ValueError, TypeError):
        # При ошибке возвращаем значение по умолчанию
        return default


def to_float(value, default=0.0):
    """Безопасно преобразовать значение в число с плавающей точкой.

    Принимает строки с запятой как десятичным разделителем.
    Используется для нормализации крепости и рейтинга.

    Args:
        value: Преобразуемое значение.
        default: Возвращаемое значение при ошибке конвертации.

    Returns:
        Число с плавающей точкой или default, если преобразование невозможно.
    """

    try:
        # Поддерживаем числа, записанные через запятую
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        # При ошибке возвращаем значение по умолчанию
        return default


def to_list(value):
    """Преобразовать значение в список тегов.

    Если в JSON уже список — возвращает нормализованный список.
    Если строка — разделяет её по запятым.

    Args:
        value: Список или строка тегов, либо None.

    Returns:
        Список строк без пустых значений и лишних пробелов.
    """

    # Отсутствующее значение превращаем в пустой список
    if value is None:
        return []

    # Готовый список только очищаем от пустых значений
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    # Строку делим на отдельные теги по запятым
    return [item.strip() for item in str(value).split(",") if item.strip()]


def load_catalog_from_json(filename="beermood_database.json"):
    """Загрузить каталог пива из JSON-файла.

    Файл ищется в той же директории, что и модуль.

    Args:
        filename: Имя JSON-файла с каталогом.

    Returns:
        Список объектов Beer, построенных из данных файла.
    """

    # Ищем файл рядом с исходным кодом программы
    file_path = Path(__file__).parent / filename

    # Загружаем записи из JSON
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Здесь будет готовый каталог объектов Beer
    catalog = []

    # Преобразуем каждую запись словаря в объект Beer
    for item in data:
        beer = Beer(
            name=str(item.get("name", "Без названия")),
            beer_type=str(item.get("beer_type", "Не указан")),
            price=to_int(item.get("price")),
            strength=to_float(item.get("strength")),
            rating=to_float(item.get("rating")),
            taste_tags=to_list(item.get("taste_tags")),
            mood_tags=to_list(item.get("mood_tags")),
            weather_tags=to_list(item.get("weather_tags"))
        )

        # Добавляем созданный напиток в каталог
        catalog.append(beer)

    return catalog

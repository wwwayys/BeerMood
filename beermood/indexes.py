from filters import normalize


def build_taste_index(catalog):
    """Построить инвертированный индекс для быстрого поиска по вкусовым тегам.

    Пример результата:
    {
        "кислое": [Beer1, Beer2],
        "лёгкое": [Beer3, Beer4]
    }

    Args:
        catalog: Список объектов Beer.

    Returns:
        Словарь, где ключи — нормализованные вкусовые теги,
        значения — списки напитков с этим тегом.
    """

    # Ключом будет вкус, значением — список подходящих напитков
    taste_index = {}

    # Просматриваем вкусовые теги каждого напитка
    for beer in catalog:
        for tag in beer.taste_tags:
            # Приводим тег к единому виду
            normalized_tag = normalize(tag)

            # Для нового тега создаём пустой список
            if normalized_tag not in taste_index:
                taste_index[normalized_tag] = []

            # Добавляем напиток в список этого вкуса
            taste_index[normalized_tag].append(beer)

    return taste_index

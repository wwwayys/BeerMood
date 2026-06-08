def normalize(text):
    """Привести текст к нижнему регистру и убрать лишние пробелы.

    Args:
        text: Исходная строка или значение, приводимое к строке.

    Returns:
        Нормализованная строка.
    """

    # Приводим любое значение к строке, убираем пробелы и регистр
    return str(text).strip().lower()


def parse_filter_values(text):
    """Разбить строку фильтра на список нормализованных значений.

    Например:
    'весёлое, спокойное, пикник'

    станет:

    ['весёлое', 'спокойное', 'пикник']

    Args:
        text: Строка с одним или несколькими значениями через запятую.

    Returns:
        Список нормализованных непустых строк.
    """

    # Сначала разделяем ввод пользователя по запятым
    values = []
    parts = str(text).split(",")

    # Нормализуем каждую часть и пропускаем пустые значения
    for part in parts:
        value = normalize(part)

        if value:
            values.append(value)

    return values


def count_matching_tags(beer, needed_tags, field_name):
    """Подсчитать количество совпадений тегов пользователя с тегами напитка.

    Args:
        beer: Объект Beer для проверки.
        needed_tags: Список нормализованных тегов пользователя.
        field_name: Имя атрибута Beer (taste_tags, mood_tags, weather_tags).

    Returns:
        Количество тегов из needed_tags, найденных у напитка.
    """

    # Получаем нужное поле и приводим его теги к единому виду
    beer_tags = getattr(beer, field_name)
    normalized_beer_tags = {normalize(tag) for tag in beer_tags}

    # Считаем совпадения с запросом пользователя
    count = 0

    for tag in needed_tags:
        if tag in normalized_beer_tags:
            count += 1

    return count


def filter_by_ranked_tags(beers, user_input, field_name):
    """Отфильтровать напитки по тегам и отсортировать по точности совпадения.

    Сначала идут напитки с наибольшим числом совпадений, при равном числе —
    с более высоким рейтингом. Напитки без совпадений не включаются.

    Args:
        beers: Список напитков для фильтрации.
        user_input: Строка с одним или несколькими тегами через запятую.
        field_name: Имя атрибута Beer (taste_tags, mood_tags, weather_tags).

    Returns:
        Список напитков, отсортированных по убыванию числа совпадений.
    """

    # Разбираем пользовательский ввод на отдельные теги
    needed_tags = parse_filter_values(user_input)

    # Без тегов возвращаем копию исходного списка
    if not needed_tags:
        return beers.copy()

    # Временно храним число совпадений, рейтинг и сам напиток
    ranked_result = []

    for beer in beers:
        match_count = count_matching_tags(beer, needed_tags, field_name)

        # Напитки без совпадений в результат не добавляем
        if match_count > 0:
            ranked_result.append((match_count, beer.rating, beer))

    # Сначала сортируем по совпадениям, затем по рейтингу
    ranked_result.sort(
        key=lambda item: (item[0], item[1]),
        reverse=True
    )

    # Убираем служебные значения и оставляем только напитки
    return [beer for match_count, rating, beer in ranked_result]


def remove_duplicates(beers):
    """Убрать повторяющиеся объекты из списка напитков.

    Сравнение ведётся по идентификатору объекта, порядок первых вхождений сохраняется.

    Args:
        beers: Список объектов Beer, возможно с повторами.

    Returns:
        Список без дублирующихся объектов с сохранением исходного порядка.
    """

    # В списке храним результат, а в множестве — уже встреченные id
    unique_beers = []
    used_ids = set()

    for beer in beers:
        beer_id = id(beer)

        # Добавляем объект только при первом появлении
        if beer_id not in used_ids:
            unique_beers.append(beer)
            used_ids.add(beer_id)

    return unique_beers


def intersect_with_current(candidates, current_results):
    """Оставить только напитки, присутствующие в текущем отфильтрованном списке.

    Порядок candidates сохраняется. Пересечение проводится по идентификатору объекта.

    Args:
        candidates: Список кандидатов, порядок которых нужно сохранить.
        current_results: Текущий список напитков, задающий ограничение.

    Returns:
        Подсписок candidates, содержащий только элементы из current_results.
    """

    # Создаём множество id напитков из текущего списка
    current_ids = {id(beer) for beer in current_results}

    result = []

    # Сохраняем только кандидатов, которые есть в текущем результате
    for beer in candidates:
        if id(beer) in current_ids:
            result.append(beer)

    return result
